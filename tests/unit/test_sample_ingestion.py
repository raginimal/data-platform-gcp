import io
import unittest
from unittest.mock import Mock

from google.api_core.exceptions import GoogleAPICallError, NotFound
from google.cloud import bigquery

from src.ingest_samples import (
    IngestionError,
    SampleFile,
    _job_id,
    ingest_one,
    ingest_samples,
    parse_gcs_csv_uri,
    validate_csv_header,
)


class SampleIngestionTests(unittest.TestCase):
    def setUp(self):
        self.source = SampleFile("sales", "gs://sample-bucket/incoming/sales.csv")
        self.blob = Mock()
        self.blob.generation = 123
        self.blob.open.side_effect = lambda *args, **kwargs: io.StringIO(
            "order_id,total\n"
        )
        self.storage = Mock()
        self.storage.bucket.return_value.blob.return_value = self.blob
        self.bigquery = Mock()
        self.bigquery.get_job.side_effect = NotFound("missing")

    def test_parse_gcs_csv_uri(self):
        self.assertEqual(
            parse_gcs_csv_uri("gs://bucket/path/sales.csv"),
            ("bucket", "path/sales.csv"),
        )

    def test_rejects_non_csv_or_wildcard_uris(self):
        for uri in (
            "https://bucket/sales.csv",
            "gs://bucket/path/*.csv",
            "gs://bucket/path/sales.txt",
        ):
            with self.subTest(uri=uri), self.assertRaises(IngestionError):
                parse_gcs_csv_uri(uri)

    def test_validate_csv_header_rejects_duplicate_columns(self):
        with self.assertRaisesRegex(IngestionError, "duplicate"):
            validate_csv_header(io.StringIO("id,ID\n"), "sales")

    def test_loads_csv_with_append_and_autodetect(self):
        job = Mock(output_rows=4, error_result=None)
        job.result.return_value = None
        self.bigquery.load_table_from_uri.return_value = job

        rows = ingest_one(self.storage, self.bigquery, "raw", self.source)

        self.assertEqual(rows, 4)
        self.bigquery.load_table_from_uri.assert_called_once()
        args, kwargs = self.bigquery.load_table_from_uri.call_args
        self.assertEqual(args, (self.source.uri, "raw.sales"))
        self.assertEqual(kwargs["job_id"], _job_id(self.source.uri, 123, "raw.sales"))
        config = kwargs["job_config"]
        self.assertEqual(config.source_format, bigquery.SourceFormat.CSV)
        self.assertTrue(config.autodetect)
        self.assertEqual(config.skip_leading_rows, 1)
        self.assertEqual(config.max_bad_records, 0)
        self.assertEqual(
            config.write_disposition,
            bigquery.WriteDisposition.WRITE_APPEND,
        )
        self.assertEqual(config.labels["source_generation"], "123")

    def test_reuses_existing_successful_job(self):
        job = Mock(output_rows=4, error_result=None)
        job.result.return_value = None
        self.bigquery.get_job.side_effect = None
        self.bigquery.get_job.return_value = job

        self.assertEqual(
            ingest_one(self.storage, self.bigquery, "raw", self.source),
            4,
        )
        self.bigquery.load_table_from_uri.assert_not_called()
        job.result.assert_called_once()

    def test_rejects_invalid_header_before_loading(self):
        self.blob.open.side_effect = lambda *args, **kwargs: io.StringIO(
            "order_id,order_id\n"
        )

        with self.assertRaisesRegex(IngestionError, "duplicate"):
            ingest_one(self.storage, self.bigquery, "raw", self.source)

        self.bigquery.load_table_from_uri.assert_not_called()

    def test_rejects_unknown_table_before_accessing_cloud_resources(self):
        source = SampleFile("other", "gs://sample-bucket/other.csv")

        with self.assertRaisesRegex(IngestionError, "sales or customers"):
            ingest_one(self.storage, self.bigquery, "raw", source)

        self.storage.bucket.assert_not_called()
        self.bigquery.get_job.assert_not_called()

    def test_reports_missing_cloud_storage_object(self):
        self.blob.reload.side_effect = NotFound("missing")

        with self.assertRaisesRegex(IngestionError, "not found or is inaccessible"):
            ingest_one(self.storage, self.bigquery, "raw", self.source)

        self.bigquery.load_table_from_uri.assert_not_called()

    def test_reports_bigquery_load_failure_without_payload_details(self):
        job = Mock(output_rows=None, error_result=None)
        job.result.side_effect = GoogleAPICallError("load service error")
        self.bigquery.load_table_from_uri.return_value = job

        with self.assertRaisesRegex(IngestionError, "inspect job"):
            ingest_one(self.storage, self.bigquery, "raw", self.source)

    def test_continues_to_customers_after_sales_failure(self):
        customers = SampleFile("customers", "gs://sample-bucket/customers.csv")
        self.bigquery.get_job.side_effect = [
            NotFound("missing"),
            NotFound("missing"),
        ]
        failed_job = Mock(output_rows=None, error_result=None)
        failed_job.result.side_effect = GoogleAPICallError("failure")
        success_job = Mock(output_rows=2, error_result=None)
        success_job.result.return_value = None
        self.bigquery.load_table_from_uri.side_effect = [failed_job, success_job]

        failures = ingest_samples(
            self.storage, self.bigquery, "raw", [self.source, customers]
        )

        self.assertEqual(failures, ["sales"])
        self.assertEqual(self.bigquery.load_table_from_uri.call_count, 2)


if __name__ == "__main__":
    unittest.main()
