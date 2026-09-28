"""DuckDB Analytical Storage and Query Engine for Technology Value Intelligence."""

from pathlib import Path
from typing import Any, Dict, List, Optional
import duckdb
import numpy as np
import pandas as pd

from tvi.config import Config, load_config


class TVIDatabase:
    """Manages DuckDB embedded analytical database operations."""

    def __init__(self, db_path: str | Path | None = None):
        from tvi.config import get_project_root
        if str(db_path) == ":memory:":
            self.db_path = Path(":memory:")
            self.conn = duckdb.connect(":memory:")
            return

        cfg = load_config()
        raw_db = Path(db_path or cfg.database.path)
        if not raw_db.is_absolute():
            self.db_path = (get_project_root() / raw_db).resolve()
        else:
            self.db_path = raw_db.resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.conn = duckdb.connect(str(self.db_path))
        except duckdb.IOException as e:
            if "lock" in str(e).lower():
                # Another process (e.g. Streamlit app) holds the file lock; fallback to in-memory database
                self.conn = duckdb.connect(":memory:")
                gen_dir = get_project_root() / "data" / "generated"
                if gen_dir.exists():
                    self.load_csv_data(gen_dir)
            else:
                raise

    def init_schema(self) -> None:
        """Initialize tables and relational views."""
        # Tables will be populated via bulk CSV read or CTAS
        pass

    def load_csv_data(self, data_dir: str | Path | None = None) -> None:
        """Load all CSV files from the generated data directory into DuckDB tables."""
        from tvi.config import get_project_root
        cfg = load_config()
        raw_dir = Path(data_dir or cfg.data.generated_dir)
        if not raw_dir.is_absolute():
            src_dir = (get_project_root() / "data" / "generated" if "generated" in str(raw_dir) else get_project_root() / raw_dir).resolve()
        else:
            src_dir = raw_dir.resolve()
        if not src_dir.exists():
            raise FileNotFoundError(f"Data directory '{src_dir}' does not exist.")

        for csv_file in src_dir.glob("*.csv"):
            table_name = csv_file.stem
            # Replace table with clean CSV import
            self.conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            self.conn.execute(
                f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{csv_file}', header=True)"
            )

        self._create_views()

    def _create_views(self) -> None:
        """Create analytical convenience views."""
        # View 1: Application monthly fully burdened cost summary
        self.conn.execute("""
            CREATE OR REPLACE VIEW v_app_monthly_cost AS
            SELECT
                month,
                application_id,
                service_id,
                business_unit_id,
                SUM(amount) AS total_cost,
                SUM(CASE WHEN cost_category = 'Software' THEN amount ELSE 0 END) AS software_cost,
                SUM(CASE WHEN cost_category = 'People' THEN amount ELSE 0 END) AS people_cost,
                SUM(CASE WHEN cost_category = 'Cloud' THEN amount ELSE 0 END) AS cloud_cost,
                SUM(CASE WHEN cost_category = 'Infrastructure' THEN amount ELSE 0 END) AS infra_cost
            FROM cost_records
            WHERE application_id IS NOT NULL
            GROUP BY month, application_id, service_id, business_unit_id
        """)

        # View 2: Application Annual TCO
        self.conn.execute("""
            CREATE OR REPLACE VIEW v_app_annual_tco AS
            SELECT
                c.application_id,
                a.application_name,
                a.service_id,
                s.service_name,
                a.lifecycle_status,
                a.criticality,
                a.annual_license_cost,
                SUM(c.amount) AS annual_tco,
                SUM(CASE WHEN c.cost_category = 'Software' THEN c.amount ELSE 0 END) AS software_tco,
                SUM(CASE WHEN c.cost_category = 'People' THEN c.amount ELSE 0 END) AS people_tco,
                SUM(CASE WHEN c.cost_category = 'Cloud' THEN c.amount ELSE 0 END) AS cloud_tco,
                SUM(CASE WHEN c.cost_category = 'Infrastructure' THEN c.amount ELSE 0 END) AS infra_tco
            FROM cost_records c
            JOIN applications a ON c.application_id = a.application_id
            JOIN it_services s ON a.service_id = s.service_id
            GROUP BY c.application_id, a.application_name, a.service_id, s.service_name, a.lifecycle_status, a.criticality, a.annual_license_cost
        """)

        # View 3: Monthly aggregated consumption
        self.conn.execute("""
            CREATE OR REPLACE VIEW v_app_monthly_consumption AS
            SELECT
                month,
                application_id,
                SUM(active_users) AS total_active_users,
                SUM(transactions) AS total_transactions,
                SUM(api_calls) AS total_api_calls,
                SUM(compute_hours) AS total_compute_hours,
                SUM(storage_gb) AS total_storage_gb,
                SUM(tickets) AS total_tickets
            FROM consumption_records
            GROUP BY month, application_id
        """)

    def query_df(self, query: str, params: Optional[List[Any]] = None) -> pd.DataFrame:
        """Execute SQL query and return pandas DataFrame."""
        if params:
            return self.conn.execute(query, params).fetchdf()
        return self.conn.execute(query).fetchdf()

    def get_entity_counts(self) -> Dict[str, int]:
        """Fetch row counts across all managed tables."""
        tables = [
            "business_units", "business_capabilities", "it_services",
            "applications", "technologies", "vendors", "projects",
            "cost_records", "consumption_records", "benefits", "kpis",
        ]
        counts = {}
        for t in tables:
            try:
                res = self.conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()
                counts[t] = res[0] if res else 0
            except Exception:
                counts[t] = 0
        return counts

    def get_total_cost(self) -> float:
        """Calculate total enterprise technology expenditure."""
        res = self.conn.execute("SELECT SUM(amount) FROM cost_records").fetchone()
        return float(res[0]) if res and res[0] is not None else 0.0

    def get_cost_by_category(self) -> pd.DataFrame:
        """Retrieve total cost broken down by cost category."""
        return self.query_df("""
            SELECT cost_category, SUM(amount) AS total_cost,
                   ROUND(SUM(amount) * 100.0 / SUM(SUM(amount)) OVER(), 2) AS percentage
            FROM cost_records
            GROUP BY cost_category
            ORDER BY total_cost DESC
        """)

    def get_cost_by_application(self, limit: int = 15) -> pd.DataFrame:
        """Retrieve top applications by technology expenditure."""
        return self.query_df(f"""
            SELECT c.application_id, a.application_name, a.lifecycle_status,
                   SUM(c.amount) AS total_cost
            FROM cost_records c
            JOIN applications a ON c.application_id = a.application_id
            GROUP BY c.application_id, a.application_name, a.lifecycle_status
            ORDER BY total_cost DESC
            LIMIT {limit}
        """)

    def get_cost_by_business_unit(self) -> pd.DataFrame:
        """Retrieve technology expenditure assigned to each business unit."""
        return self.query_df("""
            SELECT b.business_unit_id, b.business_unit_name, SUM(c.amount) AS total_cost
            FROM cost_records c
            JOIN business_units b ON c.business_unit_id = b.business_unit_id
            GROUP BY b.business_unit_id, b.business_unit_name
            ORDER BY total_cost DESC
        """)

    def get_cost_by_service(self) -> pd.DataFrame:
        """Retrieve technology expenditure by IT service."""
        return self.query_df("""
            SELECT s.service_id, s.service_name, s.service_category, SUM(c.amount) AS total_cost
            FROM cost_records c
            JOIN it_services s ON c.service_id = s.service_id
            GROUP BY s.service_id, s.service_name, s.service_category
            ORDER BY total_cost DESC
        """)

    def get_monthly_cost_trend(self) -> pd.DataFrame:
        """Retrieve monthly technology expenditure time series."""
        return self.query_df("""
            SELECT month, SUM(amount) AS total_cost
            FROM cost_records
            GROUP BY month
            ORDER BY month ASC
        """)

    def export_to_parquet(self, output_dir: str | Path | None = None) -> List[str]:
        """Export all warehouse base tables to Snappy-compressed Parquet files.

        Enables zero-copy columnar storage interoperable with Apache Arrow and external query engines.
        """
        from tvi.config import get_project_root
        target = Path(output_dir or (get_project_root() / "data" / "parquet")).resolve()
        target.mkdir(parents=True, exist_ok=True)

        tables_df = self.query_df(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main' AND table_type = 'BASE TABLE'"
        )
        exported = []
        for tbl in tables_df["table_name"]:
            out_file = target / f"{tbl}.parquet"
            self.conn.execute(
                f"COPY {tbl} TO '{out_file}' (FORMAT PARQUET, COMPRESSION SNAPPY)"
            )
            exported.append(str(out_file))
        return exported

    def query_arrow(self, sql: str):
        """Execute analytical SQL query and return zero-copy Apache Arrow Table.

        Eliminates Python object conversion overhead for large columnar aggregations.
        """
        return self.conn.execute(sql).arrow().read_all()

    def ingest_telemetry_batch(
        self, records: pd.DataFrame | List[Dict[str, Any]], deduplicate: bool = True
    ) -> int:
        """Stream micro-batch telemetry records into the analytical warehouse.

        Supports incremental streaming ingestion with idempotent deduplication.
        """
        batch_df = pd.DataFrame(records) if isinstance(records, list) else records.copy()
        if batch_df.empty:
            return 0

        if deduplicate:
            existing_ids = set(self.query_df("SELECT consumption_id FROM consumption_records")["consumption_id"])
            batch_df = batch_df[~batch_df["consumption_id"].isin(existing_ids)]
            if batch_df.empty:
                return 0

        # Register temp view and insert
        self.conn.register("tmp_telemetry_batch", batch_df)
        self.conn.execute("INSERT INTO consumption_records SELECT * FROM tmp_telemetry_batch")
        self.conn.unregister("tmp_telemetry_batch")
        return len(batch_df)

    def benchmark_queries(self, iterations: int = 5) -> Dict[str, Any]:
        """Benchmark analytical DuckDB queries across aggregation, windowing, and joins.

        Measures query latency (ms), execution consistency, and record throughput.
        """
        import time

        benchmarks = {
            "q1_annual_tco_aggregation": """
                SELECT a.application_name, s.service_name, SUM(c.amount) AS total_tco
                FROM cost_records c
                JOIN applications a ON c.application_id = a.application_id
                JOIN it_services s ON a.service_id = s.service_id
                GROUP BY a.application_name, s.service_name
            """,
            "q2_monthly_unit_economics_window": """
                SELECT c.month, c.application_id, SUM(c.amount) AS cost,
                       AVG(u.active_users) AS users,
                       SUM(u.transactions) AS txns,
                       SUM(c.amount) / NULLIF(SUM(u.transactions), 0) AS cost_per_txn
                FROM cost_records c
                JOIN consumption_records u ON c.application_id = u.application_id AND c.month = u.month
                GROUP BY c.month, c.application_id
            """,
            "q3_capability_cost_attribution": """
                SELECT cap.capability_name, SUM(c.amount * 0.70) AS attributed_cost
                FROM cost_records c
                JOIN rel_app_capability r ON c.application_id = r.application_id
                JOIN business_capabilities cap ON r.capability_id = cap.capability_id
                GROUP BY cap.capability_name
            """,
        }

        results = {}
        for q_name, query_sql in benchmarks.items():
            durations = []
            row_count = 0
            for _ in range(iterations):
                t0 = time.perf_counter()
                res = self.conn.execute(query_sql).fetchall()
                durations.append((time.perf_counter() - t0) * 1000)
                row_count = len(res)

            results[q_name] = {
                "avg_ms": round(float(np.mean(durations)), 3),
                "min_ms": round(float(np.min(durations)), 3),
                "max_ms": round(float(np.max(durations)), 3),
                "std_ms": round(float(np.std(durations)), 3),
                "result_rows": row_count,
            }

        return results

    def apply_migrations(
        self, migrations: List[Dict[str, str]] | None = None
    ) -> List[str]:
        """Apply schema version control migrations to local analytical warehouse.

        Tracks migration history in `_schema_migrations` table for auditable DDL evolution.
        """
        # Ensure migration table exists
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS _schema_migrations (
                version VARCHAR PRIMARY KEY,
                description VARCHAR,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        default_migrations = [
            {
                "version": "v2_001_finops_indexes",
                "description": "Add index on cost records application and month",
                "sql": "CREATE INDEX IF NOT EXISTS idx_cost_app_month ON cost_records (application_id, month)",
            },
            {
                "version": "v2_002_audit_log_table",
                "description": "Create financial audit log table for allocation tracking",
                "sql": """
                    CREATE TABLE IF NOT EXISTS financial_audit_log (
                        audit_id VARCHAR PRIMARY KEY,
                        entity_type VARCHAR,
                        entity_id VARCHAR,
                        change_type VARCHAR,
                        pre_amount DOUBLE,
                        post_amount DOUBLE,
                        logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """,
            },
            {
                "version": "v2_003_cloud_cur_table",
                "description": "Create cloud billing line-item ingestion table",
                "sql": """
                    CREATE TABLE IF NOT EXISTS cloud_billing_records (
                        line_item_id VARCHAR PRIMARY KEY,
                        bill_invoice_id VARCHAR,
                        month VARCHAR,
                        cloud_provider VARCHAR,
                        line_item_product_code VARCHAR,
                        pricing_unit VARCHAR,
                        usage_amount DOUBLE,
                        line_item_unblended_cost DOUBLE,
                        line_item_currency_code VARCHAR,
                        resource_id VARCHAR,
                        application_id VARCHAR
                    )
                """,
            },
        ]

        active_migrations = migrations or default_migrations
        applied_now = []

        existing_versions = set(
            self.query_df("SELECT version FROM _schema_migrations")["version"]
        )

        for mig in active_migrations:
            v = mig["version"]
            if v not in existing_versions:
                self.conn.execute(mig["sql"])
                self.conn.execute(
                    "INSERT INTO _schema_migrations (version, description) VALUES (?, ?)",
                    [v, mig["description"]],
                )
                applied_now.append(v)

        return applied_now

    def close(self) -> None:
        """Close active DuckDB connection."""
        self.conn.close()


_DB_INSTANCE: Optional[TVIDatabase] = None


def get_database(db_path: str | Path | None = None) -> TVIDatabase:
    """Singleton-style database provider."""
    global _DB_INSTANCE
    if _DB_INSTANCE is None:
        _DB_INSTANCE = TVIDatabase(db_path)
    return _DB_INSTANCE
