import argparse
import csv
import hashlib
import logging
import re
from dataclasses import dataclass
from typing import TextIO
from urllib.parse import urlsplit

from google.api_core.exceptions import GoogleAPICallError, NotFound
from google.cloud import bigquery, storage
from google.auth.exceptions import GoogleAuthError


LOGGER = logging.getLogger(__name__)


class IngestionError(Exception):
    """Raised when a source cannot be safely loaded into BigQuery."""


@dataclass(frozen=True)
class SampleFile:
    table: str
    uri: str


def parse_gcs_csv_uri(uri: str) -> tuple[str, str]:
    parsed = urlsplit(uri)
    object_name = parsed.path.lstrip("/")
    if (
        parsed.scheme != "gs"
        or not parsed.netloc
        or not object_name
        or parsed.query
        or parsed.fragment
        or "*" in object_name
        or not object_name.lower().endswith(".csv")
    ):
        raise IngestionError("Each source must be a single gs:// URI to a CSV object.")
    return parsed.netloc, object_name


def validate_csv_header(stream: TextIO, table: str) -> None:
    try:
        header = next(csv.reader(stream), None)
    except (csv.Error, UnicodeDecodeError) as error:
        raise IngestionError(f"{table} source has an unreadable CSV header.") from error

    if not header or any(not column or column != column.strip() for column in header):
        raise IngestionError(f"{table} source has an empty or invalid CSV header.")
    normalized = [column.casefold() for column in header]
    if len(set(normalized)) != len(normalized):
        raise IngestionError(f"{table} source has duplicate CSV column names.")


def _read_source_generation(
    storage_client: storage.Client, source: SampleFile
) -> tuple[str, int]:
    bucket_name, object_name = parse_gcs_csv_uri(source.uri)
    blob = storage_client.bucket(bucket_name).blob(object_name)
    try:
        blob.reload()
        if blob.generation is None:
            raise IngestionError(f"{source.table} source has no object generation.")
        generation = int(blob.generation)
        with blob.open("rt", encoding="utf-8-sig", newline="") as stream:
            validate_csv_header(stream, source.table)
    except NotFound as error:
        raise IngestionError(
            f"{source.table} source object was not found or is inaccessible."
        ) from error
    except GoogleAPICallError as error:
        raise IngestionError(
            f"Could not validate the {source.table} source object in Cloud Storage."
        ) from error
    except (csv.Error, UnicodeDecodeError) as error:
        raise IngestionError(
            f"{source.table} source has an unreadable CSV header."
        ) from error
    return object_name, generation


def _job_id(source_uri: str, generation: int, target: str) -> str:
    identity = f"{source_uri}\0{generation}\0{target}".encode("utf-8")
    return f"sample_csv_{hashlib.sha256(identity).hexdigest()[:40]}"


def ingest_one(
    storage_client: storage.Client,
    bigquery_client: bigquery.Client,
    dataset: str,
    source: SampleFile,
    project: str | None = None,
    location: str | None = None,
) -> int:
    if source.table not in {"sales", "customers"}:
        raise IngestionError("The sample table must be sales or customers.")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,1023}", dataset):
        raise IngestionError("The raw BigQuery dataset name is invalid.")

    _, generation = _read_source_generation(storage_client, source)
    target = f"{dataset}.{source.table}"
    job_id = _job_id(source.uri, generation, target)

    try:
        job = bigquery_client.get_job(job_id, project=project, location=location)
    except NotFound:
        job = None
    except GoogleAPICallError as error:
        raise IngestionError(
            f"Could not check the prior BigQuery job for {source.table}."
        ) from error

    if job is None:
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True,
            max_bad_records=0,
            create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            labels={
                "ingestion": "sample",
                "source_format": "csv",
                "source_generation": str(generation),
            },
        )
        try:
            job = bigquery_client.load_table_from_uri(
                source.uri,
                target,
                job_id=job_id,
                job_config=job_config,
                location=location,
            )
        except GoogleAPICallError as error:
            raise IngestionError(
                f"Could not start the BigQuery load for {source.table}."
            ) from error

    try:
        job.result()
    except GoogleAPICallError as error:
        raise IngestionError(
            f"BigQuery load failed for {source.table}; inspect job {job_id}."
        ) from error
    if job.error_result:
        raise IngestionError(
            f"BigQuery load failed for {source.table}; inspect job {job_id}."
        )
    return int(job.output_rows or 0)


def ingest_samples(
    storage_client: storage.Client,
    bigquery_client: bigquery.Client,
    dataset: str,
    sources: list[SampleFile],
    project: str | None = None,
    location: str | None = None,
) -> list[str]:
    failed_tables = []
    for source in sources:
        try:
            rows = ingest_one(
                storage_client,
                bigquery_client,
                dataset,
                source,
                project=project,
                location=location,
            )
        except IngestionError as error:
            LOGGER.error("%s ingestion failed: %s", source.table, error)
            failed_tables.append(source.table)
        else:
            LOGGER.info(
                "%s ingestion completed: %d rows loaded into %s.%s",
                source.table,
                rows,
                dataset,
                source.table,
            )
    return failed_tables


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load sample sales and customer CSV objects into raw BigQuery tables."
    )
    parser.add_argument("--sales-uri", required=True, help="GCS URI for the sales CSV.")
    parser.add_argument(
        "--customers-uri", required=True, help="GCS URI for the customers CSV."
    )
    parser.add_argument("--dataset", required=True, help="Existing raw BigQuery dataset.")
    parser.add_argument("--project", help="Google Cloud project; defaults to ADC.")
    parser.add_argument("--location", help="BigQuery job location.")
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    arguments = _arguments()
    try:
        storage_client = storage.Client(project=arguments.project)
        bigquery_client = bigquery.Client(project=arguments.project)
    except GoogleAuthError:
        LOGGER.error("Google Cloud credentials could not be initialized.")
        return 1

    failed_tables = ingest_samples(
        storage_client,
        bigquery_client,
        arguments.dataset,
        [
            SampleFile(table="sales", uri=arguments.sales_uri),
            SampleFile(table="customers", uri=arguments.customers_uri),
        ],
        project=arguments.project,
        location=arguments.location,
    )
    return 1 if failed_tables else 0


if __name__ == "__main__":
    raise SystemExit(main())
