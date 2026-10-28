import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.data_platform.ingest_samples import (
    CUSTOMERS,
    _load_table,
    _require_dataset_expiration,
    main,
    validate_sample_files,
)


class SampleIngestionTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp_dir.name)
        self.customers_path = self.directory / "customers.csv"
        self.sales_path = self.directory / "sales.csv"
        self.write_customers(
            [
                ["customer_id", "customer_segment", "signup_date", "country_code"],
                ["C001", "consumer", "2025-01-15", "AU"],
                ["C002", "business", "2025-02-20", "NZ"],
            ]
        )
        self.write_sales(
            [
                ["sale_id", "customer_id", "sale_date", "amount", "currency"],
                ["S001", "C001", "2025-03-01", "12.50", "AUD"],
                ["S002", "C002", "2025-03-02", "0", "NZD"],
            ]
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_customers(self, rows):
        self._write_csv(self.customers_path, rows)

    def write_sales(self, rows):
        self._write_csv(self.sales_path, rows)

    @staticmethod
    def _write_csv(path, rows):
        with path.open("w", encoding="utf-8", newline="") as csv_file:
            csv.writer(csv_file).writerows(rows)

    def test_valid_files_return_row_counts(self):
        self.assertEqual(
            validate_sample_files(self.customers_path, self.sales_path),
            {"customers": 2, "sales": 2},
        )

    def test_rejects_unexpected_headers(self):
        self.write_sales(
            [
                ["sale_id", "customer_id", "sale_date", "amount"],
                ["S001", "C001", "2025-03-01", "12.50"],
            ]
        )
        with self.assertRaisesRegex(ValueError, "expected CSV headers"):
            validate_sample_files(self.customers_path, self.sales_path)

    def test_rejects_blank_required_values(self):
        self.write_customers(
            [
                ["customer_id", "customer_segment", "signup_date", "country_code"],
                ["C001", "", "2025-01-15", "AU"],
            ]
        )
        with self.assertRaisesRegex(ValueError, "required values cannot be blank"):
            validate_sample_files(self.customers_path, self.sales_path)

    def test_rejects_invalid_dates(self):
        self.write_sales(
            [
                ["sale_id", "customer_id", "sale_date", "amount", "currency"],
                ["S001", "C001", "20250301", "12.50", "AUD"],
            ]
        )
        with self.assertRaisesRegex(ValueError, "sale_date must use YYYY-MM-DD"):
            validate_sample_files(self.customers_path, self.sales_path)

    def test_rejects_duplicate_sale_ids(self):
        self.write_sales(
            [
                ["sale_id", "customer_id", "sale_date", "amount", "currency"],
                ["S001", "C001", "2025-03-01", "12.50", "AUD"],
                ["S001", "C002", "2025-03-02", "5.00", "NZD"],
            ]
        )
        with self.assertRaisesRegex(ValueError, "duplicate sale_id"):
            validate_sample_files(self.customers_path, self.sales_path)

    def test_rejects_sales_for_unknown_customers(self):
        self.write_sales(
            [
                ["sale_id", "customer_id", "sale_date", "amount", "currency"],
                ["S001", "C999", "2025-03-01", "12.50", "AUD"],
            ]
        )
        with self.assertRaisesRegex(ValueError, "customer_id does not exist"):
            validate_sample_files(self.customers_path, self.sales_path)

    def test_rejects_invalid_amounts(self):
        self.write_sales(
            [
                ["sale_id", "customer_id", "sale_date", "amount", "currency"],
                ["S001", "C001", "2025-03-01", "1e30", "AUD"],
            ]
        )
        with self.assertRaisesRegex(ValueError, "non-negative NUMERIC"):
            validate_sample_files(self.customers_path, self.sales_path)

    def test_load_uses_explicit_schema_and_empty_destination(self):
        from google.cloud import bigquery

        class Job:
            output_rows = 2

            def result(self):
                return self

        class Client:
            def load_table_from_file(self, file_obj, destination, job_config, rewind):
                self.content = file_obj.read()
                self.destination = destination
                self.job_config = job_config
                self.rewind = rewind
                return Job()

        client = Client()
        self.assertEqual(
            _load_table(client, "demo-project", "raw", self.customers_path, CUSTOMERS),
            2,
        )
        self.assertEqual(client.destination, "demo-project.raw.customers")
        self.assertTrue(client.rewind)
        self.assertEqual(client.job_config.write_disposition, bigquery.WriteDisposition.WRITE_EMPTY)
        self.assertFalse(client.job_config.autodetect)
        self.assertEqual(
            [(field.name, field.field_type, field.mode) for field in client.job_config.schema],
            [
                ("customer_id", "STRING", "REQUIRED"),
                ("customer_segment", "STRING", "REQUIRED"),
                ("signup_date", "DATE", "REQUIRED"),
                ("country_code", "STRING", "REQUIRED"),
            ],
        )

    def test_requires_dataset_table_expiration(self):
        class Dataset:
            default_table_expiration_ms = None

        class Client:
            def get_dataset(self, dataset_id):
                self.dataset_id = dataset_id
                return Dataset()

        client = Client()
        with self.assertRaisesRegex(RuntimeError, "default table expiration"):
            _require_dataset_expiration(client, "demo-project", "raw")
        self.assertEqual(client.dataset_id, "demo-project.raw")

    def test_dry_run_does_not_create_bigquery_client(self):
        from src.data_platform.ingest_samples import DEFAULT_CUSTOMERS_CSV, DEFAULT_SALES_CSV

        with patch(
            "src.data_platform.ingest_samples._create_bigquery_client",
            side_effect=AssertionError("dry-run must not contact GCP"),
        ):
            self.assertEqual(
                main(
                    [
                        "--customers-csv",
                        str(DEFAULT_CUSTOMERS_CSV),
                        "--sales-csv",
                        str(DEFAULT_SALES_CSV),
                        "--dry-run",
                    ]
                ),
                0,
            )


if __name__ == "__main__":
    unittest.main()
