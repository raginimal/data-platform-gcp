# Source

Place application code here. Keep stack-specific conventions in the selected overlay.

## Sample BigQuery ingestion

The `data_platform.ingest_samples` CLI validates the synthetic CSVs under `sample_data/`
and loads them into `raw.customers` and `raw.sales`. See
[`docs/adr/ADR-0002-local-csv-to-bigquery-raw.md`](../docs/adr/ADR-0002-local-csv-to-bigquery-raw.md)
and [`docs/data-contracts/raw-sample-data.yaml`](../docs/data-contracts/raw-sample-data.yaml)
for the proposed demo decision and data contract.

Install the constrained dependency from the repository root:

```bash
python -m pip install -r requirements.txt
```

Validate without cloud access:

```bash
python -m src.data_platform.ingest_samples --dry-run
```

To load, set `GOOGLE_CLOUD_PROJECT` and authenticate with approved Application Default
Credentials, then run:

```bash
python -m src.data_platform.ingest_samples --dataset raw --location <bigquery-location>
```

The target dataset must already exist. The loader validates both files before contacting
GCP and requires the dataset to have a default table expiration configured. It creates
tables only when missing and refuses to append to or replace populated tables. Configure
and approve retention before loading, and use only these synthetic fixtures unless another
data source is explicitly approved. This CLI implements a
development/demo path, not the production Cloud Storage landing workflow.
