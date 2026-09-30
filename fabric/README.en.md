# Microsoft Fabric Artifacts

> Technical documentation of workspace items managed as code via Fabric Git Integration (DataOps).

[Português](README.md) | [English](README.en.md)

---

## Overview

This directory contains the declarative codebase for all **Microsoft Fabric** components supporting the Marketing Budget Optimization platform.

Unlike traditional BI environments relying on opaque binary files, all items in this workspace leverage modern, open formats native to the Fabric ecosystem (PySpark Python files, JSON configurations, PBIP report structure, and TMDL tabular model definitions). This approach enables continuous source control, peer pull-request reviews, and systematic change auditing.

---

## Workspace Directory Structure

```
fabric/
├── lakehouse/
│   └── lh_marketing_analytics.Lakehouse/         # Central unified Lakehouse (OneLake)
│
├── notebooks/
│   ├── nb_01_data_profiling.Notebook/            # Exploratory data profiling & validation
│   ├── nb_02_bronze_to_silver.Notebook/          # Schema casting, cleaning & KPI recalculation
│   ├── nb_03_silver_to_gold.Notebook/            # Analytical aggregations & summary tables
│   ├── nb_04_gold_star_schema.Notebook/          # Star Schema dimensional modeling
│   └── nb_05_data_quality.Notebook/              # Automated testing framework & Quality Gate
│
├── pipelines/
│   └── pl_ingest_marketing_campaigns.DataPipeline/  # End-to-end master orchestration pipeline
│
├── semantic_models/
│   └── sm_marketing_analytics.SemanticModel/     # DirectLake semantic model in TMDL code
│
└── reports/
    └── Marketing Analytics | Budget Optimization.Report/  # Power BI analytical report (PBIP)
```

---

## 1. Lakehouse (`lakehouse/`)

The primary Lakehouse **`lh_marketing_analytics`** resides on Microsoft **OneLake** and implements the standard Medallion architecture:

* **`Files/` Storage Section (Unmanaged Raw Storage):**
  * `Files/bronze/raw/`: Landing zone for the raw ingestion dataset `tech_advertising_campaigns_dataset.csv`.
* **`Tables/` Storage Section (Managed Delta Lake Tables):**
  * **Silver Layer:** `silver_marketing_campaigns` (cleansed, explicitly typed table with full transaction versioning via Delta Log).
  * **Gold Layer:** 7 pre-aggregated summary tables for high-performance querying (`gold_campaign_performance`, `gold_platform_performance`, `gold_objective_performance`, `gold_device_performance`, `gold_creative_performance`, `gold_placement_performance`, `gold_audience_performance`).
  * **Star Schema:** Normalized dimensional model featuring 1 central fact table `fact_campaign_performance` and 8 conforming dimensions (`dim_date`, `dim_platform`, `dim_device`, `dim_objective`, `dim_creative`, `dim_audience`, `dim_placement`, `dim_industry`).

---

## 2. PySpark Notebooks (`notebooks/`)

The notebooks contain Apache Spark transformation scripts (`notebook-content.py`) driving data processing across all tiers:

| Notebook | Layer | Technical Objective | Delta Output |
|:---|:---|:---|:---|
| **nb_01_data_profiling** | Bronze | Exploratory analysis covering null distributions, cardinality, ID uniqueness, and IQR outlier detection. | Textual profiling report |
| **nb_02_bronze_to_silver** | Bronze → Silver | Explicit type casting, safe KPI recalculation with divide-by-zero guards, and funnel consistency filtering. | `silver_marketing_campaigns` |
| **nb_03_silver_to_gold** | Silver → Gold | Multi-dimensional analytical aggregations constructed via parameterized PySpark functions. | 7 aggregated `gold_*` tables |
| **nb_04_gold_star_schema** | Gold → Dimensional | Surrogate key generation (`monotonically_increasing_id`), attribute normalization, and fact table assembly with FKs. | 1 Fact + 8 Dimensions |
| **nb_05_data_quality** | Governance | Automated test execution (completeness, uniqueness, referential anti-joins) with an auditable Quality Gate decision. | Delta audit log table |

---

## 3. Orchestration Pipeline (`pipelines/`)

The **`pl_ingest_marketing_campaigns`** data pipeline coordinates sequential execution across engineering activities:

```
Run_Data_Profiling (nb_01)
       │ (On Success)
       ▼
Run_Bronze_to_Silver (nb_02)
       │ (On Success)
       ▼
Run_Silver_to_Gold (nb_03)
       │ (On Success)
       ▼
Run_Gold_Star_Schema (nb_04)
```

* **Idempotency:** All table writes use `.mode("overwrite")`, ensuring recurring executions do not duplicate rows or produce inconsistencies.
* **Failure Handling:** If an upstream transformation fails, the pipeline aborts immediately, preventing corrupted data from entering reporting layers.

---

## 4. DirectLake Semantic Model (`semantic_models/`)

The **`sm_marketing_analytics`** semantic model queries Delta Parquet files directly through **DirectLake** mode, avoiding traditional scheduled imports and data duplication into Power BI cache.

* **TMDL (Tabular Model Definition Language) Architecture:** The semantic model is tracked as version-controlled text in the `definition/` directory:
  * `model.tmdl`: Global model metadata and table declarations.
  * `relationships.tmdl`: Explicit 1:N relationship constraints connecting fact and dimension keys.
  * `tables/_Medidas.tmdl`: Central measure repository (28+ DAX measures categorized into: Financeiro, Performance, Volume, and Formatação folders).
  * `tables/dim_*.tmdl` & `fact_*.tmdl`: Column schemas, display attributes, and sort-by bindings.

---

## 5. Power BI Report (`reports/`)

The **`Marketing Analytics | Budget Optimization`** report follows the PBIP (Power BI Project) layout format serialized under `definition/pages/`:

* **Page 1: Executivo:** Macro-level visibility into ad spend, revenue, net profit, ROAS, and customer acquisition cost (CPA) with time-series efficiency tracking.
* **Page 2: Campanhas:** In-depth tactical diagnostics, creative conversion rates, device performance breakdowns, and industry vertical analysis.
* **Page 3: Orçamento:** Capital allocation matrix, revenue-to-spend gap analysis, and automated campaign triage (Scale, Maintain, Reevaluate).

---

## How to Replicate this Workspace in Fabric

1. In a Microsoft Fabric workspace with active capacity (Trial or F-SKU), open **Workspace Settings** > **Git Integration**.
2. Connect your GitHub repository and select the primary branch.
3. Fabric will automatically sync and instantiate all artifacts from this folder.
4. Upload `data/tech_advertising_campaigns_dataset.csv` to the `Files/bronze/raw/` path in the created Lakehouse.
5. Run the `pl_ingest_marketing_campaigns` pipeline.
6. Open the report in your browser to inspect the live dashboard.

---

[Back to Main Repository](../README.en.md)
