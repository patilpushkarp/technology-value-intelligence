"""Data Quality and Integrity Validation Suite.

Executes referential integrity, numeric sanity, date consistency, uniqueness,
and null checks across enterprise data tables and downstream artifacts.

Supports CLI invocation:
    python -m tvi.validation
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple
import pandas as pd

from tvi.config import Config, load_config


class DataQualityValidator:
    """Validates structural and business integrity of enterprise datasets."""

    def __init__(self, datasets: Dict[str, pd.DataFrame] | None = None, data_dir: str | Path | None = None):
        if datasets is not None:
            self.data = datasets
        else:
            cfg = load_config()
            target_dir = Path(data_dir or cfg.data.generated_dir)
            self.data = {}
            if target_dir.exists():
                for p in target_dir.glob("*.csv"):
                    self.data[p.stem] = pd.read_csv(p)

    def validate_all(self) -> Dict[str, Any]:
        """Run all data quality checks and return a structured summary.

        Returns:
            Dict[str, Any]: Summary dictionary with pass/fail status and issue logs.
        """
        issues: List[str] = []

        if not self.data:
            return {"status": "FAIL", "issues": ["No datasets available to validate."]}

        # 1. Uniqueness / Duplicate Detection
        primary_keys = {
            "business_units": "business_unit_id",
            "business_capabilities": "capability_id",
            "it_services": "service_id",
            "applications": "application_id",
            "technologies": "technology_id",
            "vendors": "vendor_id",
            "projects": "project_id",
            "benefits": "benefit_id",
            "kpis": "kpi_id",
            "cost_records": "cost_id",
            "consumption_records": "consumption_id",
        }

        for table, pk in primary_keys.items():
            if table in self.data:
                df = self.data[table]
                dups = df[df[pk].duplicated()]
                if not dups.empty:
                    issues.append(f"Table '{table}' contains {len(dups)} duplicate values for PK '{pk}'.")

        # 2. Null Checks on Required IDs
        for table, pk in primary_keys.items():
            if table in self.data:
                df = self.data[table]
                null_count = df[pk].isnull().sum()
                if null_count > 0:
                    issues.append(f"Table '{table}' contains {null_count} nulls in PK '{pk}'.")

        # 3. Numeric Integrity (non-negative costs, users, txns)
        if "cost_records" in self.data:
            df = self.data["cost_records"]
            neg_costs = df[df["amount"] < 0]
            if not neg_costs.empty:
                issues.append(f"Found {len(neg_costs)} negative cost records.")

        if "consumption_records" in self.data:
            df = self.data["consumption_records"]
            for col in ["active_users", "transactions", "api_calls", "compute_hours", "storage_gb", "tickets"]:
                if col in df.columns:
                    neg_vals = df[df[col] < 0]
                    if not neg_vals.empty:
                        issues.append(f"Consumption table contains {len(neg_vals)} negative values in '{col}'.")

        # 4. Date Integrity (End date >= Start date)
        if "projects" in self.data:
            df = self.data["projects"]
            invalid_dates = df[pd.to_datetime(df["end_date"]) < pd.to_datetime(df["start_date"])]
            if not invalid_dates.empty:
                issues.append(f"Found {len(invalid_dates)} projects where end_date < start_date.")

        # 5. Referential Integrity Checks
        bu_ids = set(self.data["business_units"]["business_unit_id"]) if "business_units" in self.data else set()
        cap_ids = set(self.data["business_capabilities"]["capability_id"]) if "business_capabilities" in self.data else set()
        srv_ids = set(self.data["it_services"]["service_id"]) if "it_services" in self.data else set()
        app_ids = set(self.data["applications"]["application_id"]) if "applications" in self.data else set()
        tech_ids = set(self.data["technologies"]["technology_id"]) if "technologies" in self.data else set()
        ven_ids = set(self.data["vendors"]["vendor_id"]) if "vendors" in self.data else set()
        prj_ids = set(self.data["projects"]["project_id"]) if "projects" in self.data else set()

        if "business_capabilities" in self.data:
            orphan_bu = self.data["business_capabilities"][~self.data["business_capabilities"]["business_unit_id"].isin(bu_ids)]
            if not orphan_bu.empty:
                issues.append(f"Capabilities reference {len(orphan_bu)} invalid business_unit_ids.")

        if "applications" in self.data:
            orphan_srv = self.data["applications"][~self.data["applications"]["service_id"].isin(srv_ids)]
            if not orphan_srv.empty:
                issues.append(f"Applications reference {len(orphan_srv)} invalid service_ids.")

        if "rel_app_technology" in self.data:
            orphan_app = self.data["rel_app_technology"][~self.data["rel_app_technology"]["application_id"].isin(app_ids)]
            orphan_tech = self.data["rel_app_technology"][~self.data["rel_app_technology"]["technology_id"].isin(tech_ids)]
            if not orphan_app.empty or not orphan_tech.empty:
                issues.append("rel_app_technology contains orphaned application or technology keys.")

        if "rel_app_capability" in self.data:
            orphan_app = self.data["rel_app_capability"][~self.data["rel_app_capability"]["application_id"].isin(app_ids)]
            orphan_cap = self.data["rel_app_capability"][~self.data["rel_app_capability"]["capability_id"].isin(cap_ids)]
            if not orphan_app.empty or not orphan_cap.empty:
                issues.append("rel_app_capability contains orphaned application or capability keys.")

        if "cost_records" in self.data:
            df = self.data["cost_records"]
            valid_app_costs = df[df["application_id"].notnull()]
            orphan_apps = valid_app_costs[~valid_app_costs["application_id"].isin(app_ids)]
            if not orphan_apps.empty:
                issues.append(f"Cost records reference {len(orphan_apps)} unknown application_ids.")

        status = "PASS" if not issues else "FAIL"
        return {
            "status": status,
            "total_checks": 5,
            "issues": issues,
            "record_counts": {k: len(v) for k, v in self.data.items()},
        }


def run_data_quality_checks() -> Dict[str, Any]:
    """Execute complete validation suite and return report."""
    validator = DataQualityValidator()
    return validator.validate_all()


def main():
    """CLI entrypoint for validation testing."""
    config = load_config()

    # Step 1: Ensure data is generated if missing
    gen_path = Path(config.data.generated_dir)
    if not gen_path.exists() or not list(gen_path.glob("*.csv")):
        from tvi.data_generation import EnterpriseDataGenerator
        gen = EnterpriseDataGenerator(config)
        gen.generate_all()

    # Step 2: Validate Data
    data_res = run_data_quality_checks()
    data_pass = data_res["status"] == "PASS"
    print(f"Data validation: {'PASS' if data_pass else 'FAIL'}")
    if not data_pass:
        for iss in data_res["issues"]:
            print(f"  - {iss}")

    # Step 3: Validate Database
    db_pass = False
    try:
        from tvi.database import get_database
        db = get_database(config.database.path)
        db.init_schema()
        db.load_csv_data(config.data.generated_dir)
        counts = db.get_entity_counts()
        if counts.get("applications", 0) > 0 and counts.get("cost_records", 0) > 0:
            db_pass = True
        print(f"Database validation: {'PASS' if db_pass else 'FAIL'}")
    except Exception as e:
        print(f"Database validation: FAIL ({e})")

    # Step 4: Validate Graph
    graph_pass = False
    try:
        from tvi.graph import build_knowledge_graph, validate_graph
        G = build_knowledge_graph(config.data.generated_dir)
        val = validate_graph(G)
        if val["is_valid"]:
            graph_pass = True
        print(f"Graph validation: {'PASS' if graph_pass else 'FAIL'}")
    except Exception as e:
        print(f"Graph validation: FAIL ({e})")

    # Step 5: Validate Analytics
    analytics_pass = False
    try:
        from tvi.cost_analytics import calculate_application_tco, calculate_capability_cost
        from tvi.value_realization import calculate_benefit_realization
        tco_df = calculate_application_tco()
        cap_cost_df = calculate_capability_cost()
        ben_df = calculate_benefit_realization()
        if not tco_df.empty and not cap_cost_df.empty and not ben_df.empty:
            analytics_pass = True
        print(f"Analytics validation: {'PASS' if analytics_pass else 'FAIL'}")
    except Exception as e:
        print(f"Analytics validation: FAIL ({e})")

    if data_pass and db_pass and graph_pass and analytics_pass:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
