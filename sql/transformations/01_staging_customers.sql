-- Transform raw customers into the staging dataset.
-- Replace ${GCP_PROJECT_ID} before submission as part of the reviewed deployment.
CREATE OR REPLACE TABLE `${GCP_PROJECT_ID}.staging.customers` AS
SELECT
  customer_id,
  NULLIF(TRIM(name), '') AS customer_name,
  signup_date
FROM `${GCP_PROJECT_ID}.raw.customers`
WHERE customer_id IS NOT NULL
  AND NULLIF(TRIM(name), '') IS NOT NULL
  AND signup_date IS NOT NULL;
