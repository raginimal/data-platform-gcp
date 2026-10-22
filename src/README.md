# Source

Place application code here. Keep stack-specific conventions in the selected overlay.

## Demo CSV loader

`load_sample_csv.py` loads a headered CSV from Cloud Storage into an empty BigQuery table,
then verifies the expected row count and column names. It uses Google Cloud Application
Default Credentials; credentials must be configured outside the repository with the
designated identity for the demo development environment only. The GCP roles, bucket
and dataset locations, and runtime Python minimum version are TBD and must be confirmed
before use.

Install the runtime dependency with `pip install -r requirements.txt`, then provide the
project and resource names once the demo configuration is confirmed:

```text
python -m src.load_sample_csv \
  --project GCP_PROJECT_ID \
  --source-uri gs://BUCKET/OBJECT.csv \
  --table PROJECT.DATASET.TABLE \
  --expected-rows ROW_COUNT \
  --expected-columns COLUMN_1,COLUMN_2
```

Replace the uppercase placeholder values with project-owner-confirmed values; all are TBD.
No GCP project, bucket, object, dataset, table, schema, or expected row count is configured
in this repository. This first version expects a header row and lets BigQuery infer column
types; confirm the CSV header and type contract before use. The Cloud Storage bucket and
BigQuery dataset must use the same location; the selected location is TBD. The loader
refuses to append to or overwrite a non-empty destination table. A failed post-load
verification leaves the loaded table in place for review; it is not automatically deleted.

The `google-cloud-bigquery` dependency is sourced from the official Google Cloud Python
client distribution (Apache-2.0). Its purpose is BigQuery load-job and table-metadata API
access; dependency owner and approval are TBD. It grants authenticated code access to
configured cloud resources, so use least-privilege Application Default Credentials and
review transitive dependencies. The supported major version is constrained in
`requirements.txt`; review and test updates before changing that range.

Policy basis: ARCH-DEP-001, ARCH-DEP-003 through ARCH-DEP-005, SEC-IAM-001, SEC-IAM-003,
SEC-SEC-001, DATA-001, DATA-002, DATA-005, and DATA-CON-003.
