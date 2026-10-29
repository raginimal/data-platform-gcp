import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TRANSFORMATIONS = ROOT / "sql" / "transformations"
QUALITY = ROOT / "sql" / "data_quality"


class TransformationSqlTests(unittest.TestCase):
    def read_sql(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def test_staging_transformations_use_raw_sources_and_required_filters(self):
        customers = self.read_sql(TRANSFORMATIONS / "01_staging_customers.sql")
        sales = self.read_sql(TRANSFORMATIONS / "02_staging_sales.sql")

        self.assertIn("staging.customers", customers)
        self.assertIn("raw.customers", customers)
        self.assertIn("NULLIF(TRIM(name), '')", customers)
        self.assertIn("customer_id IS NOT NULL", customers)
        self.assertIn("staging.sales", sales)
        self.assertIn("raw.sales", sales)
        self.assertIn("amount >= 0", sales)
        self.assertIn("sale_id IS NOT NULL", sales)

    def test_curated_transformation_aggregates_sales_per_customer(self):
        curated = self.read_sql(TRANSFORMATIONS / "03_curated_customer_sales.sql")

        self.assertIn("curated.customer_sales", curated)
        self.assertIn("staging.customers", curated)
        self.assertIn("staging.sales", curated)
        self.assertIn("COUNT(sale.sale_id)", curated)
        self.assertIn("SUM(sale.amount)", curated)
        self.assertIn("GROUP BY", curated)

    def test_quality_gate_covers_contract_invariants(self):
        quality = self.read_sql(QUALITY / "customers_and_sales.sql")

        self.assertEqual(quality.count("ASSERT ("), 4)
        self.assertIn("amount < 0", quality)
        self.assertIn("LEFT JOIN", quality)
        self.assertIn("customer.customer_id IS NULL", quality)
        self.assertIn("HAVING COUNT(*) > 1", quality)

    def test_all_sql_files_keep_project_substitution_external(self):
        for path in sorted(TRANSFORMATIONS.glob("*.sql")):
            self.assertIn("${GCP_PROJECT_ID}", self.read_sql(path))
        self.assertIn(
            "${GCP_PROJECT_ID}",
            self.read_sql(QUALITY / "customers_and_sales.sql"),
        )


if __name__ == "__main__":
    unittest.main()
