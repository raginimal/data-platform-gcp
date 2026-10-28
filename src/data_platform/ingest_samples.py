"""Validate synthetic CSV fixtures and load them into BigQuery raw tables."""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CUSTOMERS_CSV = REPOSITORY_ROOT / "sample_data" / "customers.csv"
DEFAULT_SALES_CSV = REPOSITORY_ROOT / "sample_data" / "sales.csv"


@dataclass(frozen=True)
class TableSpec:
    table_name: str
    columns: tuple[tuple[str, str], ...]


CUSTOMERS = TableSpec(
    table_name="customers",
    columns=(
        ("customer_id", "STRING"),
        ("customer_segment", "STRING"),
        ("signup_date", "DATE"),
        ("country_code", "STRING"),
    ),
)
SALES = TableSpec(
    table_name="sales",
    columns=(
        ("sale_id", "STRING"),
        ("customer_id", "STRING"),
        ("sale_date", "DATE"),
        ("amount", "NUMERIC"),
        ("currency", "STRING"),
    ),
)
TABLE_SPECS = (CUSTOMERS, SALES)


def _read_csv(path: Path, spec: TableSpec) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")

    records: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.reader(csv_file)
        headers = next(reader, None)
        expected_headers = [column for column, _ in spec.columns]
        if headers != expected_headers:
            raise ValueError(
                f"{path}: expected CSV headers {expected_headers}, got {headers}"
            )

        for row_number, values in enumerate(reader, start=2):
            if len(values) != len(expected_headers):
                raise ValueError(
                    f"{path} row {row_number}: expected {len(expected_headers)} columns"
                )
            if any(not value.strip() for value in values):
                raise ValueError(f"{path} row {row_number}: required values cannot be blank")
            records.append(dict(zip(expected_headers, values)))

    if not records:
        raise ValueError(f"{path}: CSV must contain at least one data row")
    return records


def _validate_date(records: list[dict[str, str]], field: str, path: Path) -> None:
    for row_number, record in enumerate(records, start=2):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", record[field]):
            raise ValueError(
                f"{path} row {row_number}: {field} must use YYYY-MM-DD format"
            )
        try:
            date.fromisoformat(record[field])
        except ValueError as exc:
            raise ValueError(
                f"{path} row {row_number}: {field} must use YYYY-MM-DD format"
            ) from exc


def _validate_unique_ids(
    records: list[dict[str, str]], field: str, path: Path
) -> set[str]:
    seen: set[str] = set()
    for row_number, record in enumerate(records, start=2):
        identifier = record[field]
        if identifier in seen:
            raise ValueError(f"{path} row {row_number}: duplicate {field}")
        seen.add(identifier)
    return seen


def _validate_customers(records: list[dict[str, str]], path: Path) -> set[str]:
    customer_ids = _validate_unique_ids(records, "customer_id", path)
    _validate_date(records, "signup_date", path)
    for row_number, record in enumerate(records, start=2):
        if not re.fullmatch(r"[A-Z]{2}", record["country_code"]):
            raise ValueError(
                f"{path} row {row_number}: country_code must be a two-letter uppercase code"
            )
    return customer_ids


def _validate_sales(
    records: list[dict[str, str]], path: Path, customer_ids: set[str]
) -> None:
    _validate_unique_ids(records, "sale_id", path)
    _validate_date(records, "sale_date", path)

    for row_number, record in enumerate(records, start=2):
        if record["customer_id"] not in customer_ids:
            raise ValueError(
                f"{path} row {row_number}: customer_id does not exist in customers CSV"
            )
        if not re.fullmatch(r"[A-Z]{3}", record["currency"]):
            raise ValueError(
                f"{path} row {row_number}: currency must be a three-letter uppercase code"
            )
        try:
            amount = Decimal(record["amount"])
        except InvalidOperation as exc:
            raise ValueError(
                f"{path} row {row_number}: amount must be a non-negative decimal"
            ) from exc
        if not amount.is_finite():
            raise ValueError(
                f"{path} row {row_number}: amount must be a non-negative NUMERIC value "
                "with at most 29 integer digits and 9 decimal places"
            )
        integer_digits = max(amount.adjusted() + 1, 0) if amount else 0
        scale = max(0, -amount.as_tuple().exponent)
        if (
            amount < 0
            or integer_digits > 29
            or scale > 9
        ):
            raise ValueError(
                f"{path} row {row_number}: amount must be a non-negative NUMERIC value "
                "with at most 29 integer digits and 9 decimal places"
            )


def validate_sample_files(customers_path: Path, sales_path: Path) -> dict[str, int]:
    """Validate headers, required fields, types, identifiers, and customer references."""
    customers = _read_csv(customers_path, CUSTOMERS)
    sales = _read_csv(sales_path, SALES)
    customer_ids = _validate_customers(customers, customers_path)
    _validate_sales(sales, sales_path, customer_ids)
    return {"customers": len(customers), "sales": len(sales)}


def _create_bigquery_client(project: str, location: str | None):
    try:
        from google.cloud import bigquery
    except ImportError as exc:
        raise RuntimeError(
            "BigQuery support is missing; install the dependencies in requirements.txt"
        ) from exc

    options = {"project": project}
    if location:
        options["location"] = location
    return bigquery.Client(**options)


def _load_table(client, project: str, dataset: str, path: Path, spec: TableSpec) -> int:
    from google.cloud import bigquery

    schema = [
        bigquery.SchemaField(name, field_type, mode="REQUIRED")
        for name, field_type in spec.columns
    ]
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        schema=schema,
        autodetect=False,
        create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED,
        write_disposition=bigquery.WriteDisposition.WRITE_EMPTY,
        max_bad_records=0,
    )
    destination = f"{project}.{dataset}.{spec.table_name}"
    with path.open("rb") as csv_file:
        job = client.load_table_from_file(
            csv_file,
            destination,
            job_config=job_config,
            rewind=True,
        )
    job.result()
    if job.output_rows is None:
        raise RuntimeError(f"BigQuery load job for {destination} completed without a row count")
    return job.output_rows


def _require_dataset_expiration(client, project: str, dataset: str) -> None:
    dataset_resource = client.get_dataset(f"{project}.{dataset}")
    if not dataset_resource.default_table_expiration_ms:
        raise RuntimeError(
            f"BigQuery dataset {project}.{dataset} must have a default table "
            "expiration configured before sample data is loaded"
        )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and load the synthetic sales and customer CSVs to BigQuery."
    )
    parser.add_argument(
        "--customers-csv", type=Path, default=DEFAULT_CUSTOMERS_CSV,
        help=f"Customer CSV path (default: {DEFAULT_CUSTOMERS_CSV})",
    )
    parser.add_argument(
        "--sales-csv", type=Path, default=DEFAULT_SALES_CSV,
        help=f"Sales CSV path (default: {DEFAULT_SALES_CSV})",
    )
    parser.add_argument(
        "--project",
        default=os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCLOUD_PROJECT"),
        help="GCP project ID (defaults to GOOGLE_CLOUD_PROJECT or GCLOUD_PROJECT)",
    )
    parser.add_argument(
        "--dataset",
        default=os.getenv("BIGQUERY_RAW_DATASET", "raw"),
        help="Existing BigQuery raw dataset (default: BIGQUERY_RAW_DATASET or raw)",
    )
    parser.add_argument(
        "--location",
        default=os.getenv("BIGQUERY_LOCATION"),
        help="BigQuery dataset location (defaults to BIGQUERY_LOCATION)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the CSVs and report row counts without contacting GCP",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9_]{1,1024}", args.dataset):
        parser.error("--dataset must contain only letters, numbers, or underscores")

    row_counts = validate_sample_files(args.customers_csv, args.sales_csv)
    if args.dry_run:
        target = f"{args.project}.{args.dataset}" if args.project else args.dataset
        for spec in TABLE_SPECS:
            print(
                f"Validated {row_counts[spec.table_name]} rows for "
                f"{target}.{spec.table_name}; not loaded (dry-run)."
            )
        return 0

    if not args.project:
        parser.error(
            "--project is required unless GOOGLE_CLOUD_PROJECT or GCLOUD_PROJECT is set"
        )
    if not args.location:
        parser.error(
            "--location is required for a BigQuery load unless BIGQUERY_LOCATION is set"
        )

    client = _create_bigquery_client(args.project, args.location)
    _require_dataset_expiration(client, args.project, args.dataset)
    for spec, path in zip(TABLE_SPECS, (args.customers_csv, args.sales_csv)):
        output_rows = _load_table(client, args.project, args.dataset, path, spec)
        print(
            f"Loaded {output_rows} rows into "
            f"{args.project}.{args.dataset}.{spec.table_name}."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
