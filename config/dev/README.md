# DEV Configuration

Non-secret environment configuration belongs here. Use secret management for sensitive values.

The sample GCS-to-BigQuery raw load is configured in `ingestion.yaml`. Set
`GCP_PROJECT_ID`, `BIGQUERY_LOCATION`, and `GCS_LANDING_BUCKET`, then install
the Python 3.10+ dependencies and run these commands from the repository root:

```bash
python -m pip install -r requirements-ingestion.txt
python -m src.data_platform.ingestion.gcs_to_bigquery --config config/dev/ingestion.yaml
```

The configured customer and sales objects must be synthetic or approved
non-production CSVs matching their explicit schemas. The command appends to
the existing `raw` dataset; it does not create buckets, datasets, or an
orchestration trigger. The configured `max_attempts` bounds retries for
transient BigQuery service errors. Authenticate with Application Default
Credentials and grant only the permissions needed to read the configured GCS
objects, submit BigQuery jobs, and write to the existing raw dataset.

Keep source objects immutable as required by `ARCHITECTURE.md`. Re-running the
same object generation reuses its BigQuery job ID to avoid a second append.
After correcting a failed input, publish the corrected file as a new immutable
GCS object and update its configured URI for replay.
