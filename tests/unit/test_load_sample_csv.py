import argparse
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from src.load_sample_csv import (
    _columns,
    _non_negative_int,
    _source_uri,
    _table_id,
    build_parser,
    load_and_verify,
    make_load_job_config,
)


class LoadSampleCsvTests(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.client.load_table_from_uri.return_value = Mock()
        self.client.get_table.return_value = SimpleNamespace(
            num_rows=2,
            schema=[SimpleNamespace(name="id"), SimpleNamespace(name="category")],
        )
        self.job_config = object()

    def test_loads_and_verifies_expected_rows_and_columns(self):
        report = load_and_verify(
            self.client,
            "gs://demo-bucket/sample.csv",
            "demo-project.analytics.sample",
            2,
            ("id", "category"),
            self.job_config,
        )

        self.client.load_table_from_uri.assert_called_once_with(
            "gs://demo-bucket/sample.csv",
            "demo-project.analytics.sample",
            job_config=self.job_config,
        )
        self.client.load_table_from_uri.return_value.result.assert_called_once_with()
        self.client.get_table.assert_called_once_with("demo-project.analytics.sample")
        self.assertEqual(report.row_count, 2)
        self.assertEqual(report.columns, ("id", "category"))

    def test_fails_when_row_count_does_not_match(self):
        with self.assertRaisesRegex(ValueError, "row count mismatch.*expected 3, found 2"):
            load_and_verify(
                self.client,
                "gs://demo-bucket/sample.csv",
                "demo-project.analytics.sample",
                3,
                ("id", "category"),
                self.job_config,
            )

    def test_fails_when_columns_do_not_match(self):
        with self.assertRaisesRegex(ValueError, "missing columns: amount; unexpected columns: category"):
            load_and_verify(
                self.client,
                "gs://demo-bucket/sample.csv",
                "demo-project.analytics.sample",
                2,
                ("id", "amount"),
                self.job_config,
            )

    def test_waits_for_load_job_before_reading_destination(self):
        events = []
        job = Mock()
        job.result.side_effect = lambda: events.append("job.result")
        self.client.load_table_from_uri.side_effect = lambda *args, **kwargs: (
            events.append("load_table_from_uri") or job
        )
        self.client.get_table.side_effect = lambda table_id: (
            events.append("get_table") or SimpleNamespace(
                num_rows=2,
                schema=[SimpleNamespace(name="id"), SimpleNamespace(name="category")],
            )
        )

        load_and_verify(
            self.client,
            "gs://demo-bucket/sample.csv",
            "demo-project.analytics.sample",
            2,
            ("id", "category"),
            self.job_config,
        )

        self.assertEqual(events, ["load_table_from_uri", "job.result", "get_table"])
        job.result.assert_called_once_with()

    def test_load_job_config_uses_headered_csv_and_non_overwrite_disposition(self):
        bigquery = SimpleNamespace(
            LoadJobConfig=Mock(return_value="config"),
            SourceFormat=SimpleNamespace(CSV="CSV"),
            WriteDisposition=SimpleNamespace(WRITE_EMPTY="WRITE_EMPTY"),
        )

        self.assertEqual(make_load_job_config(bigquery), "config")
        bigquery.LoadJobConfig.assert_called_once_with(
            source_format="CSV",
            skip_leading_rows=1,
            autodetect=True,
            write_disposition="WRITE_EMPTY",
        )

    def test_cli_requires_runtime_gcp_and_validation_values(self):
        with self.assertRaises(SystemExit) as error:
            build_parser().parse_args([])

        self.assertEqual(error.exception.code, 2)

    def test_validates_source_uri_table_row_count_and_columns(self):
        self.assertEqual(_source_uri("gs://bucket/object.csv"), "gs://bucket/object.csv")
        self.assertEqual(_table_id("project.dataset.table"), "project.dataset.table")
        self.assertEqual(_non_negative_int("0"), 0)
        self.assertEqual(_columns("id, category"), ("id", "category"))

        for value, validator in (
            ("https://bucket/object.csv", _source_uri),
            ("gs://bucket", _source_uri),
            ("project.dataset", _table_id),
            ("-1", _non_negative_int),
            ("id,,category", _columns),
        ):
            with self.subTest(value=value), self.assertRaises(argparse.ArgumentTypeError):
                validator(value)

    def test_rejects_duplicate_expected_columns_before_cloud_call(self):
        with self.assertRaisesRegex(ValueError, "must not contain duplicates"):
            load_and_verify(
                self.client,
                "gs://demo-bucket/sample.csv",
                "demo-project.analytics.sample",
                2,
                ("id", "id"),
                self.job_config,
            )

        self.client.load_table_from_uri.assert_not_called()


if __name__ == "__main__":
    unittest.main()
