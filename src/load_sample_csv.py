#!/usr/bin/env python3
"""Load a headered CSV from Cloud Storage into BigQuery and verify its table."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any, Optional, Sequence, Tuple


@dataclass(frozen=True)
class LoadReport:
    table_id: str
    row_count: int
    columns: Tuple[str, ...]


def _source_uri(value: str) -> str:
    if not value.startswith("gs://"):
        raise argparse.ArgumentTypeError("source URI must be a Cloud Storage URI such as gs://bucket/object.csv")
    bucket_and_object = value[len("gs://") :]
    bucket, separator, object_name = bucket_and_object.partition("/")
    if not bucket or not separator or not object_name:
        raise argparse.ArgumentTypeError("source URI must include both a bucket and an object name")
    if any(character.isspace() for character in value):
        raise argparse.ArgumentTypeError("source URI must not contain whitespace")
    return value


def _table_id(value: str) -> str:
    parts = value.split(".")
    if len(parts) != 3 or any(not part for part in parts):
        raise argparse.ArgumentTypeError("table must be fully qualified as PROJECT.DATASET.TABLE")
    if any(character.isspace() for character in value):
        raise argparse.ArgumentTypeError("table identifier must not contain whitespace")
    return value


def _non_negative_int(value: str) -> int:
    try:
        result = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("expected row count must be an integer") from error
    if result < 0:
        raise argparse.ArgumentTypeError("expected row count must not be negative")
    return result


def _columns(value: str) -> tuple[str, ...]:
    columns = tuple(column.strip() for column in value.split(","))
    if not columns or any(not column for column in columns):
        raise argparse.ArgumentTypeError("expected columns must be a comma-separated list of names")
    if len(set(columns)) != len(columns):
        raise argparse.ArgumentTypeError("expected columns must not contain duplicates")
    return columns


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Load a headered CSV from Cloud Storage into BigQuery and verify its row count and columns."
    )
    parser.add_argument("--project", required=True, help="GCP project used for the BigQuery job")
    parser.add_argument("--source-uri", required=True, type=_source_uri, help="Cloud Storage CSV URI (gs://bucket/object)")
    parser.add_argument("--table", required=True, type=_table_id, help="destination as PROJECT.DATASET.TABLE")
    parser.add_argument("--expected-rows", required=True, type=_non_negative_int)
    parser.add_argument("--expected-columns", required=True, type=_columns, help="comma-separated column names")
    return parser


def make_load_job_config(bigquery: Any) -> Any:
    return bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_EMPTY,
    )


def load_and_verify(
    client: Any,
    source_uri: str,
    table_id: str,
    expected_rows: int,
    expected_columns: Sequence[str],
    job_config: Any,
) -> LoadReport:
    if expected_rows < 0:
        raise ValueError("expected row count must not be negative")
    if not expected_columns or any(not column for column in expected_columns):
        raise ValueError("expected columns must contain non-empty names")
    if len(set(expected_columns)) != len(expected_columns):
        raise ValueError("expected columns must not contain duplicates")

    job = client.load_table_from_uri(source_uri, table_id, job_config=job_config)
    job.result()
    table = client.get_table(table_id)

    actual_rows = table.num_rows
    actual_columns = tuple(field.name for field in table.schema)
    if actual_rows != expected_rows:
        raise ValueError(f"row count mismatch for {table_id}: expected {expected_rows}, found {actual_rows}")

    missing = sorted(set(expected_columns) - set(actual_columns))
    unexpected = sorted(set(actual_columns) - set(expected_columns))
    if missing or unexpected:
        details = []
        if missing:
            details.append(f"missing columns: {', '.join(missing)}")
        if unexpected:
            details.append(f"unexpected columns: {', '.join(unexpected)}")
        raise ValueError(f"column mismatch for {table_id}: {'; '.join(details)}")

    return LoadReport(table_id, actual_rows, actual_columns)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        from google.cloud import bigquery
    except ImportError as error:
        raise SystemExit("BigQuery client is missing; install the project dependencies with pip install -r requirements.txt") from error

    client = bigquery.Client(project=args.project)
    report = load_and_verify(
        client=client,
        source_uri=args.source_uri,
        table_id=args.table,
        expected_rows=args.expected_rows,
        expected_columns=args.expected_columns,
        job_config=make_load_job_config(bigquery),
    )
    print(
        f"Verified {report.table_id}: {report.row_count} rows; "
        f"columns: {', '.join(report.columns)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
