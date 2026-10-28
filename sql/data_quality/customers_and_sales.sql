-- Run after the staging transformations and before curated publication.
-- Replace ${GCP_PROJECT_ID} before submission as part of the reviewed deployment.
ASSERT (
  SELECT COUNT(*) = 0
  FROM `${GCP_PROJECT_ID}.staging.customers`
  WHERE customer_id IS NULL
     OR customer_name IS NULL
     OR signup_date IS NULL
) AS 'staging.customers contains invalid required fields';

ASSERT (
  SELECT COUNT(*) = 0
  FROM `${GCP_PROJECT_ID}.staging.sales`
  WHERE sale_id IS NULL
     OR customer_id IS NULL
     OR sale_date IS NULL
     OR amount IS NULL
     OR amount < 0
) AS 'staging.sales contains invalid required fields or amounts';

ASSERT (
  SELECT COUNT(*) = 0
  FROM `${GCP_PROJECT_ID}.staging.sales` AS sale
  LEFT JOIN `${GCP_PROJECT_ID}.staging.customers` AS customer
    ON customer.customer_id = sale.customer_id
  WHERE customer.customer_id IS NULL
) AS 'staging.sales contains an unknown customer_id';

ASSERT (
  SELECT COUNT(*) = 0
  FROM (
    SELECT sale_id
    FROM `${GCP_PROJECT_ID}.staging.sales`
    GROUP BY sale_id
    HAVING COUNT(*) > 1
  )
) AS 'staging.sales contains duplicate sale_id values';
