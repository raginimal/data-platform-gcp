"""Validate Cloud Storage objects and append them to BigQuery raw tables."""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import logging
import math
import os
import re
import sys
import time as time_module
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import date, datetime
from datetime import time as time_value
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import yaml
from google.api_core.exceptions import (
    Conflict,
    DeadlineExceeded,
    InternalServerError,
    NotFound,
    ServiceUnavailable,
    TooManyRequests,
)

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_ENV_REFERENCE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
_SUPPORTED_FORMATS = {"CSV", "NDJSON"}
_SUPPORTED_TYPES = {
    "BOOL",
    "BYTES",
    "DATE",
    "DATETIME",
    "FLOAT64",
    "INT64",
    "NUMERIC",
    "STRING",
    "TIME",
    "TIMESTAMP",
}
_RETRYABLE_ERRORS = (
    DeadlineExceeded,
    InternalServerError,
    ServiceUnavailable,
    TooManyRequests,
)
_LOGGER = logging.getLogger("data_platform.ingestion")


@dataclass(frozen=True)
class SchemaField:
    name: str
    field_type: str
    mode: str = "NULLABLE"

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not _IDENTIFIER.fullmatch(self.name):
            raise ValueError(f"Invalid schema field name: {self.name!r}")
        if not isinstance(self.field_type, str):
            raise ValueError(f"Invalid BigQuery field type: {self.field_type!r}")
        if not isinstance(self.mode, str):
            raise ValueError(f"Invalid field mode: {self.mode!r}")
        if self.field_type.upper() not in _SUPPORTED_TYPES:
            raise ValueError(f"Unsupported BigQuery field type: {self.field_type!r}")
        if self.mode.upper() not in {"NULLABLE", "REQUIRED"}:
            raise ValueError(f"Unsupported field mode: {self.mode!r}")
        object.__setattr__(self, "field_type", self.field_type.upper())
        object.__setattr__(self, "mode", self.mode.upper())


@dataclass(frozen=True)
class IngestionResult:
    source_uri: str
    source_generation: int
    target_table: str
    job_id: str
    row_count: int | None
    status: str


def _normalize_format(file_format: Any, source_number: int | None = None) -> str:
    if (
        not isinstance(file_format, str)
        or file_format.upper() not in _SUPPORTED_FORMATS
    ):
        prefix = f"Source {source_number} " if source_number is not None else ""
        raise ValueError(f"{prefix}format must be CSV or NDJSON")
    return file_format.upper()


def _expand_environment(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _expand_environment(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_expand_environment(item) for item in value]
    if not isinstance(value, str):
        return value

    def replace(match: re.Match[str]) -> str:
        variable = match.group(1)
        if variable not in os.environ:
            raise ValueError(
                f"Required configuration environment variable {variable} is not set"
            )
        return os.environ[variable]

    return _ENV_REFERENCE.sub(replace, value)


def load_config(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"Unable to read ingestion configuration {path}") from exc

    if not isinstance(config, dict):
        raise ValueError("Ingestion configuration must be a YAML mapping")
    config = _expand_environment(config)

    project_id = config.get("project_id")
    raw_dataset = config.get("raw_dataset")
    sources = config.get("sources")
    if not isinstance(project_id, str) or not project_id.strip():
        raise ValueError("Configuration must specify project_id")
    if not isinstance(raw_dataset, str) or not _IDENTIFIER.fullmatch(raw_dataset):
        raise ValueError(
            "Configuration raw_dataset must be a valid BigQuery dataset identifier"
        )
    if not isinstance(sources, list) or not sources:
        raise ValueError("Configuration must include at least one source")

    location = config.get("location")
    if location is not None and (not isinstance(location, str) or not location.strip()):
        raise ValueError(
            "Configuration location must be a non-empty string when specified"
        )
    max_attempts = config.get("max_attempts", 3)
    if (
        not isinstance(max_attempts, int)
        or isinstance(max_attempts, bool)
        or max_attempts < 1
    ):
        raise ValueError("Configuration max_attempts must be a positive integer")

    validated_sources: list[dict[str, Any]] = []
    seen_tables: set[str] = set()
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            raise ValueError(f"Source {index + 1} must be a YAML mapping")
        source_uri = source.get("source_uri")
        table = source.get("table")
        file_format = _normalize_format(source.get("format"), index + 1)
        fields = source.get("schema")
        _parse_gcs_uri(source_uri)
        if not isinstance(table, str) or not _IDENTIFIER.fullmatch(table):
            raise ValueError(f"Source {index + 1} has an invalid BigQuery table name")
        if table in seen_tables:
            raise ValueError(f"Configuration contains duplicate target table {table!r}")
        seen_tables.add(table)
        if not isinstance(fields, list) or not fields:
            raise ValueError(f"Source {index + 1} must define a non-empty schema")

        schema = []
        field_names: set[str] = set()
        for field in fields:
            if not isinstance(field, dict) or not isinstance(field.get("name"), str):
                raise ValueError(f"Source {index + 1} contains an invalid schema field")
            schema_field = SchemaField(
                field["name"],
                field.get("type", ""),
                field.get("mode", "NULLABLE"),
            )
            if schema_field.name in field_names:
                raise ValueError(
                    f"Source {index + 1} contains duplicate field {schema_field.name!r}"
                )
            field_names.add(schema_field.name)
            schema.append(schema_field)

        skip_leading_rows = source.get(
            "skip_leading_rows", 1 if file_format == "CSV" else 0
        )
        if (
            not isinstance(skip_leading_rows, int)
            or isinstance(skip_leading_rows, bool)
            or skip_leading_rows < (1 if file_format == "CSV" else 0)
        ):
            minimum = 1 if file_format == "CSV" else 0
            raise ValueError(
                f"Source {index + 1} skip_leading_rows must be at least {minimum}"
            )
        if file_format == "NDJSON" and skip_leading_rows:
            raise ValueError(f"Source {index + 1} NDJSON cannot skip leading rows")

        validated_sources.append(
            {
                "source_uri": source_uri,
                "table": table,
                "format": file_format,
                "schema": schema,
                "skip_leading_rows": skip_leading_rows,
            }
        )

    return {
        "project_id": project_id,
        "location": location,
        "raw_dataset": raw_dataset,
        "max_attempts": max_attempts,
        "sources": validated_sources,
    }


def _parse_gcs_uri(source_uri: Any) -> tuple[str, str]:
    if not isinstance(source_uri, str):
        raise ValueError("Source URI must be a gs:// Cloud Storage URI")
    parsed = urlsplit(source_uri)
    if (
        parsed.scheme != "gs"
        or not parsed.netloc
        or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*[a-z0-9]", parsed.netloc)
        or len(parsed.netloc) > 222
        or not parsed.path.strip("/")
        or parsed.query
        or parsed.fragment
        or "*" in parsed.path
    ):
        raise ValueError(
            "Source URI must identify one gs://bucket/object without a wildcard"
        )
    return parsed.netloc, parsed.path[1:]


def validate_stream(
    source: Any,
    file_format: str,
    schema: Sequence[SchemaField],
    skip_leading_rows: int | None = None,
) -> int:
    if not isinstance(file_format, str):
        raise ValueError("File format must be CSV or NDJSON")
    if file_format == "CSV":
        minimum_skip_rows = 1
    elif file_format == "NDJSON":
        minimum_skip_rows = 0
    else:
        raise ValueError(f"Unsupported file format: {file_format!r}")
    if skip_leading_rows is None:
        skip_leading_rows = minimum_skip_rows
    if (
        not isinstance(skip_leading_rows, int)
        or isinstance(skip_leading_rows, bool)
        or skip_leading_rows < minimum_skip_rows
    ):
        raise ValueError(f"skip_leading_rows must be at least {minimum_skip_rows}")
    if file_format == "NDJSON" and skip_leading_rows:
        raise ValueError("NDJSON cannot skip leading rows")
    text_source = io.TextIOWrapper(source, encoding="utf-8-sig", newline="")
    if file_format == "CSV":
        row_count = _validate_csv(text_source, schema, skip_leading_rows)
    else:
        row_count = _validate_ndjson(text_source, schema)
    if row_count == 0:
        raise ValueError("Source object contains no data records")
    return row_count


def _validate_csv(
    source: Any, schema: Sequence[SchemaField], skip_leading_rows: int
) -> int:
    reader = csv.reader(source)
    try:
        headers = next(reader)
    except StopIteration as exc:
        raise ValueError("CSV source is missing its header row") from exc
    expected = [field.name for field in schema]
    if headers != expected:
        raise ValueError(f"CSV header must match schema field order: {expected}")

    row_count = 0
    for line_number, values in enumerate(reader, start=2):
        if line_number <= skip_leading_rows:
            continue
        if len(values) != len(schema):
            raise ValueError(
                f"CSV line {line_number} has a different number "
                "of values than the schema"
            )
        _validate_record(dict(zip(expected, values)), schema, line_number)
        row_count += 1
    return row_count


def _validate_ndjson(source: Any, schema: Sequence[SchemaField]) -> int:
    row_count = 0
    for line_number, line in enumerate(source, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line, object_pairs_hook=_unique_json_keys)
        except (json.JSONDecodeError, ValueError) as exc:
            raise ValueError(f"NDJSON line {line_number} is not valid JSON") from exc
        if not isinstance(record, dict):
            raise ValueError(f"NDJSON line {line_number} must contain a JSON object")
        _validate_record(record, schema, line_number)
        row_count += 1
    return row_count


def _unique_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    record: dict[str, Any] = {}
    for key, value in pairs:
        if key in record:
            raise ValueError(f"Duplicate JSON field {key!r}")
        record[key] = value
    return record


def _validate_record(
    record: dict[str, Any],
    schema: Sequence[SchemaField],
    line_number: int,
) -> None:
    expected = {field.name for field in schema}
    extra_fields = record.keys() - expected
    if extra_fields:
        raise ValueError(
            f"Record at line {line_number} contains fields not in the schema: "
            f"{sorted(extra_fields)}"
        )
    for field in schema:
        value = record.get(field.name)
        empty = value is None or value == ""
        if empty:
            if field.mode == "REQUIRED":
                raise ValueError(
                    f"Record at line {line_number} is missing required "
                    f"field {field.name!r}"
                )
            continue
        if not _matches_type(value, field.field_type):
            raise ValueError(
                f"Record at line {line_number} field {field.name!r} "
                f"does not match BigQuery type {field.field_type}"
            )


def _matches_type(value: Any, field_type: str) -> bool:
    if field_type == "STRING":
        return isinstance(value, str)
    if field_type == "INT64":
        if isinstance(value, bool):
            return False
        try:
            return str(int(value)) == str(value).strip()
        except (TypeError, ValueError, OverflowError):
            return False
    if field_type in {"NUMERIC", "FLOAT64"}:
        if isinstance(value, bool):
            return False
        try:
            number = Decimal(str(value))
            return number.is_finite() and (
                field_type != "FLOAT64" or math.isfinite(float(number))
            )
        except (InvalidOperation, ValueError, OverflowError):
            return False
    if field_type == "BOOL":
        if isinstance(value, bool):
            return True
        return isinstance(value, str) and value.lower() in {"true", "false"}
    if field_type == "DATE":
        if not isinstance(value, str):
            return False
        try:
            return date.fromisoformat(value).isoformat() == value
        except ValueError:
            return False
    if field_type in {"DATETIME", "TIMESTAMP"}:
        if not isinstance(value, str):
            return False
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if field_type == "TIMESTAMP" and parsed.utcoffset() is None:
                return False
            return True
        except ValueError:
            return False
    if field_type == "TIME":
        if not isinstance(value, str):
            return False
        try:
            time_value.fromisoformat(value)
            return True
        except ValueError:
            return False
    if field_type == "BYTES":
        if not isinstance(value, str):
            return False
        try:
            base64.b64decode(value, validate=True)
            return True
        except (ValueError, base64.binascii.Error):
            return False
    return False


class GcsToBigQueryIngestor:
    def __init__(
        self,
        storage_client: Any,
        bigquery_client: Any,
        project_id: str,
        raw_dataset: str,
        location: str | None = None,
        max_attempts: int = 3,
    ) -> None:
        if not isinstance(project_id, str) or not project_id.strip():
            raise ValueError("project_id is required")
        if not _IDENTIFIER.fullmatch(raw_dataset):
            raise ValueError("raw_dataset must be a valid BigQuery dataset identifier")
        if (
            not isinstance(max_attempts, int)
            or isinstance(max_attempts, bool)
            or max_attempts < 1
        ):
            raise ValueError("max_attempts must be a positive integer")
        self.storage_client = storage_client
        self.bigquery_client = bigquery_client
        self.project_id = project_id
        self.raw_dataset = raw_dataset
        self.location = location
        self.max_attempts = max_attempts

    def ingest(
        self,
        source_uri: str,
        target_table: str,
        schema: Sequence[SchemaField],
        file_format: str,
        skip_leading_rows: int | None = None,
    ) -> IngestionResult:
        bucket_name, object_name = _parse_gcs_uri(source_uri)
        if not isinstance(target_table, str) or not _IDENTIFIER.fullmatch(target_table):
            raise ValueError("target_table must be a valid BigQuery table identifier")
        if not schema or any(not isinstance(field, SchemaField) for field in schema):
            raise ValueError("schema must contain at least one field")
        if len({field.name for field in schema}) != len(schema):
            raise ValueError("schema field names must be unique")
        file_format = _normalize_format(file_format)
        if skip_leading_rows is None:
            skip_leading_rows = 1 if file_format == "CSV" else 0

        blob = self.storage_client.bucket(bucket_name).blob(object_name)
        blob.reload()
        generation = blob.generation
        if generation is None:
            raise ValueError(f"Cloud Storage object {source_uri!r} has no generation")
        generation = int(generation)
        target = f"{self.project_id}.{self.raw_dataset}.{target_table}"
        row_count: int | None = None
        job_id = _stable_job_id(source_uri, generation, target, schema, file_format)
        current_job_id = job_id
        _log_event(
            logging.INFO,
            "ingestion_started",
            source_uri=source_uri,
            source_generation=generation,
            target_table=target,
            job_id=job_id,
        )

        try:
            with blob.open("rb", if_generation_match=generation) as source:
                row_count = validate_stream(
                    source,
                    file_format,
                    schema,
                    skip_leading_rows=skip_leading_rows,
                )
            blob.reload()
            if int(blob.generation) != generation:
                raise ValueError(
                    f"Cloud Storage object {source_uri!r} changed during validation"
                )

            job = None
            for attempt in range(1, self.max_attempts + 1):
                attempt_job_id = job_id
                try:
                    job = self._get_or_start_load(
                        attempt_job_id,
                        source_uri,
                        target,
                        schema,
                        file_format,
                        skip_leading_rows,
                    )
                    job.result()
                    break
                except _RETRYABLE_ERRORS as exc:
                    if attempt == self.max_attempts:
                        raise
                    _log_event(
                        logging.WARNING,
                        "ingestion_retry",
                        source_uri=source_uri,
                        source_generation=generation,
                        target_table=target,
                        job_id=attempt_job_id,
                        attempt=attempt,
                        next_attempt=attempt + 1,
                        error_type=type(exc).__name__,
                    )
                    time_module.sleep(min(2 ** (attempt - 1), 30))
            if job is None:
                raise RuntimeError("Ingestion ended without a BigQuery load job")
            output_rows = getattr(job, "output_rows", None)
            result = IngestionResult(
                source_uri=source_uri,
                source_generation=generation,
                target_table=target,
                job_id=(job.job_id if getattr(job, "job_id", None) else job_id),
                row_count=output_rows if output_rows is not None else row_count,
                status="SUCCEEDED",
            )
        except Exception as exc:
            _log_event(
                logging.ERROR,
                "ingestion_failed",
                source_uri=source_uri,
                source_generation=generation,
                target_table=target,
                job_id=current_job_id,
                error_type=type(exc).__name__,
                **({"error_message": str(exc)} if isinstance(exc, ValueError) else {}),
            )
            raise

        _log_event(
            logging.INFO,
            "ingestion_succeeded",
            source_uri=result.source_uri,
            source_generation=result.source_generation,
            target_table=result.target_table,
            job_id=result.job_id,
            row_count=result.row_count,
        )
        return result

    def _get_or_start_load(
        self,
        job_id: str,
        source_uri: str,
        target: str,
        schema: Sequence[SchemaField],
        file_format: str,
        skip_leading_rows: int,
    ) -> Any:
        try:
            return self.bigquery_client.get_job(job_id, location=self.location)
        except NotFound:
            pass

        from google.cloud import bigquery

        job_config = bigquery.LoadJobConfig(
            source_format=(
                bigquery.SourceFormat.CSV
                if file_format == "CSV"
                else bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
            ),
            schema=[
                bigquery.SchemaField(field.name, field.field_type, mode=field.mode)
                for field in schema
            ],
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            autodetect=False,
            skip_leading_rows=skip_leading_rows if file_format == "CSV" else 0,
            max_bad_records=0,
            ignore_unknown_values=False,
            allow_jagged_rows=False,
        )
        try:
            return self.bigquery_client.load_table_from_uri(
                source_uri,
                target,
                job_config=job_config,
                job_id=job_id,
                location=self.location,
            )
        except Conflict:
            return self.bigquery_client.get_job(job_id, location=self.location)


def _stable_job_id(
    source_uri: str,
    generation: int,
    target: str,
    schema: Sequence[SchemaField],
    file_format: str,
) -> str:
    identity = {
        "source_uri": source_uri,
        "generation": generation,
        "target": target,
        "schema": [asdict(field) for field in schema],
        "format": file_format,
    }
    digest = hashlib.sha256(
        json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:32]
    return f"raw_ingest_{digest}"


def _log_event(level: int, event: str, **fields: Any) -> None:
    _LOGGER.log(level, json.dumps({"event": event, **fields}, sort_keys=True))


def _google_clients(project_id: str) -> tuple[Any, Any]:
    from google.cloud import bigquery, storage

    return storage.Client(project=project_id), bigquery.Client(project=project_id)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate configured Cloud Storage samples and append them "
            "to BigQuery raw."
        )
    )
    parser.add_argument(
        "--config", type=Path, required=True, help="Path to YAML ingestion config"
    )
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    try:
        config = load_config(args.config)
        storage_client, bigquery_client = _google_clients(config["project_id"])
        ingestor = GcsToBigQueryIngestor(
            storage_client,
            bigquery_client,
            project_id=config["project_id"],
            raw_dataset=config["raw_dataset"],
            location=config["location"],
            max_attempts=config["max_attempts"],
        )
        for source in config["sources"]:
            result = ingestor.ingest(
                source_uri=source["source_uri"],
                target_table=source["table"],
                schema=source["schema"],
                file_format=source["format"],
                skip_leading_rows=source["skip_leading_rows"],
            )
            print(
                f"{result.status}: {result.row_count} rows loaded to "
                f"{result.target_table} (job {result.job_id})"
            )
    except Exception as exc:
        _log_event(
            logging.ERROR,
            "ingestion_command_failed",
            error_type=type(exc).__name__,
            **({"error_message": str(exc)} if isinstance(exc, ValueError) else {}),
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
