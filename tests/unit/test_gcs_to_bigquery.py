import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from google.api_core.exceptions import BadRequest, NotFound, ServiceUnavailable
from google.cloud import bigquery as bigquery_sdk

from src.data_platform.ingestion.gcs_to_bigquery import (
    GcsToBigQueryIngestor,
    SchemaField,
    load_config,
    validate_stream,
)


class FakeBlob:
    generation = 123

    def __init__(self, contents):
        self.contents = contents
        self.open_generation = None

    def reload(self):
        pass

    def open(self, mode, if_generation_match=None):
        if mode != "rb":
            raise ValueError("Expected a binary read")
        self.open_generation = if_generation_match
        return io.BytesIO(self.contents)


class FakeBucket:
    def __init__(self, blob):
        self._blob = blob

    def blob(self, object_name):
        self.object_name = object_name
        return self._blob


class FakeStorageClient:
    def __init__(self, blob):
        self._bucket = FakeBucket(blob)

    def bucket(self, bucket_name):
        self.bucket_name = bucket_name
        return self._bucket


class FakeJob:
    output_rows = 2

    def __init__(self, error=None):
        self.error = error

    def result(self):
        if self.error is not None:
            raise self.error
        return None


class FakeBigQueryClient:
    def __init__(self):
        self.loaded = []
        self.jobs = {}
        self.failures_remaining = 0
        self.load_attempts = 0
        self.job_error = None

    def get_job(self, job_id, location=None):
        if job_id not in self.jobs:
            raise NotFound("job not found")
        return self.jobs[job_id]

    def load_table_from_uri(
        self, source_uri, target, job_config, job_id, location=None
    ):
        self.load_attempts += 1
        if self.failures_remaining:
            self.failures_remaining -= 1
            raise ServiceUnavailable("temporary service failure")
        job = FakeJob(self.job_error)
        self.loaded.append((source_uri, target, job_config, job_id, location))
        self.jobs[job_id] = job
        return job


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.schema = [
            SchemaField("record_id", "INT64", "REQUIRED"),
            SchemaField("name", "STRING"),
            SchemaField("active", "BOOL"),
        ]

    def test_validates_csv_records(self):
        source = io.BytesIO(b"record_id,name,active\n1,Ada,true\n2,Lin,false\n")

        self.assertEqual(validate_stream(source, "CSV", self.schema), 2)

    def test_validates_ndjson_records(self):
        source = io.BytesIO(
            b'{"record_id":1,"name":"Ada","active":true}\n'
            b'{"record_id":2,"name":null,"active":false}\n'
        )

        self.assertEqual(validate_stream(source, "NDJSON", self.schema), 2)

    def test_rejects_bad_headers_required_values_and_types(self):
        cases = [
            (b"name,record_id,active\nAda,1,true\n", "header must match"),
            (b"record_id,name,active\n,Ada,true\n", "required field"),
            (b"record_id,name,active\nnot-an-int,Ada,true\n", "INT64"),
        ]
        for contents, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(ValueError, message):
                    validate_stream(io.BytesIO(contents), "CSV", self.schema)

    def test_rejects_extra_fields_and_duplicate_json_keys(self):
        with self.assertRaisesRegex(ValueError, "not in the schema"):
            validate_stream(
                io.BytesIO(b'{"record_id":1,"name":"Ada","active":true,"other":2}\n'),
                "NDJSON",
                self.schema,
            )
        with self.assertRaisesRegex(ValueError, "not valid JSON"):
            validate_stream(
                io.BytesIO(b'{"record_id":1,"record_id":2}\n'),
                "NDJSON",
                self.schema,
            )

    def test_rejects_empty_source(self):
        with self.assertRaisesRegex(ValueError, "no data records"):
            validate_stream(
                io.BytesIO(b"record_id,name,active\n"),
                "CSV",
                self.schema,
            )


class ConfigurationTests(unittest.TestCase):
    def test_expands_environment_and_validates_sources(self):
        contents = """
project_id: demo-project
location: US
raw_dataset: raw
sources:
  - source_uri: gs://${GCS_BUCKET}/samples/data.csv
    table: sample
    format: CSV
    schema:
      - name: record_id
        type: INT64
        mode: REQUIRED
"""
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "ingestion.yaml"
            config_path.write_text(contents, encoding="utf-8")
            with patch.dict(os.environ, {"GCS_BUCKET": "demo-landing"}):
                config = load_config(config_path)

        self.assertEqual(
            config["sources"][0]["source_uri"], "gs://demo-landing/samples/data.csv"
        )
        self.assertEqual(
            config["sources"][0]["schema"],
            [SchemaField("record_id", "INT64", "REQUIRED")],
        )

    def test_reports_missing_environment_variables(self):
        contents = """
project_id: demo-project
raw_dataset: raw
sources:
  - source_uri: gs://${MISSING_BUCKET}/samples/data.csv
    table: sample
    format: CSV
    schema:
      - name: record_id
        type: INT64
"""
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "ingestion.yaml"
            config_path.write_text(contents, encoding="utf-8")
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaisesRegex(ValueError, "MISSING_BUCKET"):
                    load_config(config_path)


class IngestionTests(unittest.TestCase):
    def test_validates_gcs_object_then_appends_to_raw_with_stable_job_id(self):
        contents = b"record_id,name,active\n1,Ada,true\n2,Lin,false\n"
        blob = FakeBlob(contents)
        storage = FakeStorageClient(blob)
        bigquery = FakeBigQueryClient()
        ingestor = GcsToBigQueryIngestor(
            storage,
            bigquery,
            project_id="demo-project",
            raw_dataset="raw",
            location="US",
        )
        schema = [
            SchemaField("record_id", "INT64", "REQUIRED"),
            SchemaField("name", "STRING"),
            SchemaField("active", "BOOL"),
        ]

        result = ingestor.ingest(
            "gs://demo-landing/samples/records.csv",
            "records",
            schema,
            "CSV",
        )
        replay = ingestor.ingest(
            "gs://demo-landing/samples/records.csv",
            "records",
            schema,
            "CSV",
        )

        self.assertEqual(result.status, "SUCCEEDED")
        self.assertEqual(replay.job_id, result.job_id)
        self.assertEqual(result.row_count, 2)
        self.assertEqual(result.source_generation, 123)
        self.assertEqual(blob.open_generation, 123)
        self.assertEqual(storage._bucket.object_name, "samples/records.csv")
        self.assertEqual(bigquery.loaded[0][1], "demo-project.raw.records")
        self.assertEqual(bigquery.loaded[0][0], "gs://demo-landing/samples/records.csv")
        self.assertEqual(bigquery.loaded[0][3], result.job_id)
        self.assertEqual(bigquery.loaded[0][4], "US")
        self.assertEqual(len(bigquery.loaded), 1)
        job_config = bigquery.loaded[0][2]
        self.assertEqual(job_config.source_format, bigquery_sdk.SourceFormat.CSV)
        self.assertEqual(
            job_config.write_disposition, bigquery_sdk.WriteDisposition.WRITE_APPEND
        )
        self.assertFalse(job_config.autodetect)
        self.assertEqual(job_config.skip_leading_rows, 1)
        self.assertEqual(
            [(field.name, field.field_type, field.mode) for field in job_config.schema],
            [
                ("record_id", "INT64", "REQUIRED"),
                ("name", "STRING", "NULLABLE"),
                ("active", "BOOL", "NULLABLE"),
            ],
        )

    def test_retries_transient_bigquery_errors_with_bounded_job_ids(self):
        blob = FakeBlob(b"record_id,name,active\n1,Ada,true\n")
        bigquery = FakeBigQueryClient()
        bigquery.failures_remaining = 1
        ingestor = GcsToBigQueryIngestor(
            FakeStorageClient(blob),
            bigquery,
            "demo-project",
            "raw",
            max_attempts=2,
        )
        schema = [
            SchemaField("record_id", "INT64", "REQUIRED"),
            SchemaField("name", "STRING"),
            SchemaField("active", "BOOL"),
        ]

        with self.assertLogs("data_platform.ingestion", level="WARNING") as captured:
            with patch("src.data_platform.ingestion.gcs_to_bigquery.time_module.sleep"):
                result = ingestor.ingest(
                    "gs://demo-landing/samples/records.csv",
                    "records",
                    schema,
                    "CSV",
                )

        self.assertEqual(bigquery.load_attempts, 2)
        self.assertEqual(result.job_id, bigquery.loaded[0][3])
        self.assertEqual(
            bigquery.loaded[0][2].write_disposition,
            bigquery_sdk.WriteDisposition.WRITE_APPEND,
        )
        retry = json.loads(captured.output[-1].split(":", 2)[-1].strip())
        self.assertEqual(retry["event"], "ingestion_retry")
        self.assertEqual(retry["attempt"], 1)

    def test_validation_failure_does_not_start_bigquery_load_and_logs_failure(self):
        blob = FakeBlob(b"wrong,header\ninvalid,data\n")
        bigquery = FakeBigQueryClient()
        ingestor = GcsToBigQueryIngestor(
            FakeStorageClient(blob), bigquery, "demo-project", "raw"
        )

        with self.assertLogs("data_platform.ingestion", level="ERROR") as captured:
            with self.assertRaisesRegex(ValueError, "header must match"):
                ingestor.ingest(
                    "gs://demo-landing/samples/records.csv",
                    "records",
                    [SchemaField("record_id", "INT64", "REQUIRED")],
                    "CSV",
                )

        self.assertEqual(bigquery.loaded, [])
        failure = json.loads(captured.output[-1].split(":", 2)[-1].strip())
        self.assertEqual(failure["event"], "ingestion_failed")
        self.assertEqual(failure["error_type"], "ValueError")

    def test_bigquery_failure_is_logged_and_propagated(self):
        blob = FakeBlob(b"record_id,name,active\n1,Ada,true\n")
        bigquery = FakeBigQueryClient()
        bigquery.job_error = BadRequest("invalid load")
        ingestor = GcsToBigQueryIngestor(
            FakeStorageClient(blob), bigquery, "demo-project", "raw"
        )
        schema = [
            SchemaField("record_id", "INT64", "REQUIRED"),
            SchemaField("name", "STRING"),
            SchemaField("active", "BOOL"),
        ]

        with self.assertLogs("data_platform.ingestion", level="ERROR") as captured:
            with self.assertRaises(BadRequest):
                ingestor.ingest(
                    "gs://demo-landing/samples/records.csv",
                    "records",
                    schema,
                    "CSV",
                )

        failure = json.loads(captured.output[-1].split(":", 2)[-1].strip())
        self.assertEqual(failure["event"], "ingestion_failed")
        self.assertEqual(failure["error_type"], "BadRequest")
        self.assertEqual(failure["job_id"], bigquery.loaded[0][3])


if __name__ == "__main__":
    unittest.main()
