# TBM / ITFM Data Model & Analytical Warehouse

**Purpose:** Ingests raw enterprise CSVs into an in-process columnar DuckDB database (database/technology_value_intelligence.duckdb). Enforces relational integrity, creates indexing, and builds high-performance analytical views for instant multi-dimensional aggregation.  
**Series Index:** Notebook 02 of 12  
**Baseline Reference:** [`./v1_baseline.ipynb`](v1_baseline.ipynb) | **Active Development:** [`./v2_development.ipynb`](v2_development.ipynb)

---

## 1. Executive Business Purpose
Ingests raw enterprise CSVs into an in-process columnar DuckDB database (database/technology_value_intelligence.duckdb). Enforces relational integrity, creates indexing, and builds high-performance analytical views for instant multi-dimensional aggregation.

### Core Methodology
In-process OLAP columnar storage via DuckDB; relational schema normalization; automated foreign key referential verification; materialized analytical views.

---

## 2. Key Scenarios & Focus Areas
- Ingestion and indexing of all master data and monthly time-series ledger/consumption records.

---

## 3. Data Dependencies & Artifacts

### Primary Inputs
- `data/raw/*.csv`

### Primary Outputs
- `database/technology_value_intelligence.duckdb`
- `Analytical views (v_app_monthly_cost, v_consumption_monthly, v_project_summary)`
- `data/parquet/*.parquet` (Snappy-compressed portable columnar tables)
- `_schema_migrations` (Version control ledger for local warehouse DDL evolutions)
- In-memory Apache Arrow table zero-copy querying interface (`query_arrow()`)

---

## 4. File Structure & Versioning

```text
02_tbm_itfm_data_model/
├── README.md               # Purpose, documentation, and improvement roadmap (this file)
├── v1_baseline.ipynb       # Untouched baseline reference notebook (self-contained)
└── v2_development.ipynb    # Working copy for iterative improvements and code extensions
```

- **`v1_baseline.ipynb`**: Preserves the verified baseline implementation with dynamic root discovery.
- **`v2_development.ipynb`**: Active development notebook expanded with Snappy Parquet exports, zero-copy Arrow queries, streaming telemetry ingestion, vectorized query benchmarks, and schema migrations.
- **Baseline Preservation:** `v1_baseline.ipynb` preserves the verified baseline implementation, while `v2_development.ipynb` is used for active evolution.

---

## 5. Iteration & Improvement Roadmap
- [x] Add Parquet export pipelines and Apache Arrow zero-copy memory transfers (`export_to_parquet()`, `query_arrow()`).
- [x] Implement incremental append ingestion for real-time telemetry streaming (`ingest_telemetry_batch()`).
- [x] Benchmark DuckDB aggregation queries against large-scale synthetic datasets (`benchmark_queries()`).
- [x] Implement schema migration and version control tooling for the local warehouse (`apply_migrations()`).
- [ ] Implement automated partition pruning on monthly date columns in Parquet lakes.
- [ ] Connect DuckDB through MotherDuck cloud bridge for hybrid edge-cloud analytical replication.
