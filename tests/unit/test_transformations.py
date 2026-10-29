import sqlite3
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TRANSFORMATIONS = ROOT / "sql" / "transformations"
QUALITY = ROOT / "sql" / "data_quality"


def run_quality_report(customers, sales):
    connection = sqlite3.connect(":memory:")
    connection.executescript(
        """
        CREATE TABLE staging_customers (
            customer_id INTEGER,
            customer_name TEXT,
            signup_date TEXT
        );
        CREATE TABLE staging_sales (
            sale_id INTEGER,
            customer_id INTEGER,
            sale_date TEXT,
            quantity INTEGER,
            unit_price NUMERIC,
            revenue NUMERIC
        );
        """
    )
    connection.executemany(
        "INSERT INTO staging_customers VALUES (?, ?, ?)", customers
    )
    connection.executemany(
        "INSERT INTO staging_sales VALUES (?, ?, ?, ?, ?, ?)", sales
    )

    sql = (QUALITY / "customers_and_sales.sql").read_text(encoding="utf-8")
    sql = sql.replace(
        "`${GCP_PROJECT_ID}.staging.customers`", "staging_customers"
    ).replace("`${GCP_PROJECT_ID}.staging.sales`", "staging_sales")
    report_sql, _ = sql.split("\nASSERT (", maxsplit=1)
    statements = [statement.strip() for statement in report_sql.split(";")]
    for statement in statements:
        if statement:
            cursor = connection.execute(statement)

    report = {
        row[0]: {
            "severity": row[1],
            "failure_count": row[2],
            "status": row[3],
        }
        for row in cursor.fetchall()
    }
    connection.close()
    return report


class TransformationSqlTests(unittest.TestCase):
    def read_sql(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def test_staging_preserves_rows_for_quality_checks(self):
        customers = self.read_sql(TRANSFORMATIONS / "01_staging_customers.sql")
        sales = self.read_sql(TRANSFORMATIONS / "02_staging_sales.sql")

        self.assertIn("staging.customers", customers)
        self.assertIn("raw.customers", customers)
        self.assertIn("NULLIF(TRIM(name), '')", customers)
        self.assertNotIn("WHERE", customers.upper())
        self.assertIn("staging.sales", sales)
        self.assertIn("raw.sales", sales)
        self.assertIn("quantity", sales)
        self.assertIn("unit_price", sales)
        self.assertIn("revenue", sales)
        self.assertNotIn("WHERE", sales.upper())

    def test_curated_transformation_aggregates_validated_revenue(self):
        curated = self.read_sql(TRANSFORMATIONS / "03_curated_customer_sales.sql")

        self.assertIn("curated.customer_sales", curated)
        self.assertIn("staging.customers", curated)
        self.assertIn("staging.sales", curated)
        self.assertIn("COUNT(sale.sale_id)", curated)
        self.assertIn("SUM(sale.revenue)", curated)
        self.assertIn("AS total_sales_amount", curated)
        self.assertIn("GROUP BY", curated)

    def test_quality_report_passes_valid_synthetic_data(self):
        customers = [
            (1, "Alice", "2024-01-01"),
            (2, "Bob", "2024-02-01"),
        ]
        sales = [
            (10, 1, "2024-03-01", 2, 3.25, 6.50),
            (11, 2, "2024-03-02", 1, 4.00, 4.00),
        ]

        report = run_quality_report(customers, sales)

        self.assertEqual(len(report), 7)
        self.assertTrue(
            all(
                result == {
                    "severity": "CRITICAL",
                    "failure_count": 0,
                    "status": "PASS",
                }
                for result in report.values()
            )
        )

    def test_quality_report_fails_invalid_synthetic_data(self):
        customers = [
            (1, "Alice", "2024-01-01"),
            (1, "Duplicate Alice", "2024-01-02"),
            (None, "Missing ID", "2024-01-03"),
        ]
        sales = [
            (10, 1, "2024-03-01", 2, 3.00, 6.00),
            (10, 1, "2024-03-02", 0, 3.00, 0.00),
            (11, 99, "2024-03-03", 2, 1.50, 2.00),
            (12, None, "2024-03-04", 1, 1.00, 1.00),
            (13, 1, "2024-03-05", 1, -1.00, -1.00),
        ]

        report = run_quality_report(customers, sales)

        expected_failures = {
            "customer_required_fields": 1,
            "duplicate_customer_ids": 1,
            "sales_required_fields": 1,
            "duplicate_sale_ids": 1,
            "valid_sales_values": 2,
            "revenue_consistency": 1,
            "customer_referential_integrity": 2,
        }
        self.assertEqual(
            {
                name: result["failure_count"]
                for name, result in report.items()
                if result["status"] == "FAIL"
            },
            expected_failures,
        )

    def test_critical_quality_failures_fail_the_bigquery_job(self):
        quality = self.read_sql(QUALITY / "customers_and_sales.sql")

        self.assertIn("ASSERT (", quality)
        self.assertIn("severity = 'CRITICAL'", quality)
        self.assertIn("status = 'FAIL'", quality)
        self.assertIn("inspect the quality report above", quality)

    def test_all_sql_files_keep_project_substitution_external(self):
        for path in sorted(TRANSFORMATIONS.glob("*.sql")):
            self.assertIn("${GCP_PROJECT_ID}", self.read_sql(path))
        self.assertIn(
            "${GCP_PROJECT_ID}",
            self.read_sql(QUALITY / "customers_and_sales.sql"),
        )


if __name__ == "__main__":
    unittest.main()
