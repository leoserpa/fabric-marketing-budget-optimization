# Architecture Guide

> Technical explanation of the architectural decisions made in the Marketing Budget Optimization project.

[Português](architecture.md) | [English](architecture.en.md)

---

## 1. Why Medallion Architecture?

The **Medallion Architecture** (Bronze → Silver → Gold) was chosen because it is the recommended pattern by Microsoft for analytical projects in Fabric, offering concrete advantages for this project:

### Separation of Concerns

```mermaid
flowchart LR
    subgraph Bronze["Bronze — Fidelity"]
        B1["Raw data exactly as received"]
        B2["No transformations applied"]
        B3["Full lineage tracking"]
    end

    subgraph Silver["Silver — Reliability"]
        S1["Standardized data types"]
        S2["Recalculated metrics"]
        S3["Quality rules applied"]
    end

    subgraph Gold["Gold — Business Value"]
        G1["Ready-to-use analytical tables"]
        G2["Aggregations by dimension"]
        G3["Star Schema for Power BI"]
    end

    Bronze --> Silver --> Gold
```

### Specific Project Benefits

| Decision | Justification |
|:---|:---|
| **Bronze preserves the original CSV** | Allows data reprocessing without requiring new ingestion |
| **Silver recalculates all metrics** | Ensures consistency without relying on formulas from the original dataset |
| **Gold separates analytical tables from the dimensional model** | `nb_03` generates exploratory aggregations; `nb_04` generates the optimized Star Schema for Power BI |

### Why not a direct approach (CSV → Power BI)?

While it might seem simpler, directly importing the CSV into Power BI would eliminate:

- Quality validation before analysis
- Traceability of transformations
- The ability to perform incremental reprocessing
- DirectLake mode (which requires Delta tables in the Lakehouse)

---

## 2. Why Star Schema?

The dimensional model was chosen over a single denormalized table for three main reasons:

### 2.1 VertiPaq Engine Optimization

Power BI uses the **VertiPaq** engine, which compresses data column by column. Dimensional tables with low cardinality (6 platforms, 5 objectives, 3 devices) compress significantly better than a flat table containing repeated text columns across 10,000 rows.

### 2.2 Multidimensional Filtering

The Star Schema allows filters in Power BI to propagate from any dimension to the fact table. A slicer for `dim_platform` automatically filters all measures without requiring additional context manipulation.

### 2.3 Maintainability

Adding a new dimension (e.g., `dim_region`) requires only:
1. Creating the table in notebook `nb_04`
2. Adding the foreign key (FK) to the fact table
3. Registering the relationship in the semantic model

```mermaid
erDiagram
    fact_campaign_performance ||--o{ dim_date : "1:N"
    fact_campaign_performance ||--o{ dim_platform : "1:N"
    fact_campaign_performance ||--o{ dim_device : "1:N"
    fact_campaign_performance ||--o{ dim_objective : "1:N"
    fact_campaign_performance ||--o{ dim_creative : "1:N"
    fact_campaign_performance ||--o{ dim_audience : "1:N"
    fact_campaign_performance ||--o{ dim_placement : "1:N"
    fact_campaign_performance ||--o{ dim_industry : "1:N"
```

### Discarded Alternative: Snowflake Schema

Normalizing dimensions into sub-dimensions (e.g., separating `operating_system` from `dim_device`) was unnecessary because:
- The data volume (10,000 records) does not justify the added complexity
- Dimensions with 2-7 attributes do not benefit from extra normalization
- DirectLake efficiently handles this data scale

---

## 3. Data Quality Strategy

Data quality is enforced in **two complementary stages**:

```mermaid
flowchart TD
    subgraph "Stage 1 — Profiling (nb_01)"
        P1["Exploratory analysis"]
        P2["Detection of nulls & duplicates"]
        P3["Business rule validation"]
        P4["Outlier analysis (IQR)"]
        P5["Verification of calculated metrics"]
    end

    subgraph "Stage 2 — Quality Gate (nb_05)"
        Q1["Completeness: nulls in PKs & FKs"]
        Q2["Uniqueness: primary keys"]
        Q3["Referential Integrity: Anti Join"]
        Q4["Business Rules: funnels and limits"]
        Q5["Consistency: recalculated metrics"]
        Q6["Granularity: 1 campaign = 1 row"]
        Q7["Quality Gate: PASSED / FAILED"]
    end

    P1 --> P2 --> P3 --> P4 --> P5
    P5 -.->|"Data Approved"| Q1
    Q1 --> Q2 --> Q3 --> Q4 --> Q5 --> Q6 --> Q7

    style Q7 fill:#1D6FA5,color:#fff
```

### Why two stages?

| Aspect | Profiling (nb_01) | Quality Gate (nb_05) |
|:---|:---|:---|
| **When it runs** | Before transformations | After the Star Schema |
| **Goal** | Understand raw data | Validate the final model |
| **Output** | Textual findings in notebook | Audit log persisted in Delta |
| **Blocking** | No (informative) | Yes (CRITICAL / WARNING) |

### Testing Framework (nb_05)

Each test logs:
- **test_id**: Unique identifier (e.g., `DQ-NUL-DATE_KEY`)
- **category**: Completeness, Uniqueness, Referential Integrity, Business Rule, Consistency
- **severity**: `CRITICAL` (blocks execution) or `WARNING` (alert only)
- **execution_date**: Timestamp for traceability

---

## 4. DirectLake Semantic Model

### What is DirectLake?

DirectLake is Power BI's highest-performing connection mode in Fabric. Unlike Import (which copies data into the model) and DirectQuery (which queries the source on every interaction), DirectLake **reads directly from Parquet/Delta files** in the Lakehouse with no data refresh required.

### Semantic Model Decisions

| Decision | Justification |
|:---|:---|
| **DAX Measures instead of Calculated Columns** | 12 out of 28 measures are aggregated metrics (SUM, DIVIDE) that must evaluate dynamically based on the filter context, not at the row level. |
| **Calculated Column `Status Orçamento`** | Justified exception: Must exist as a column to serve as a slicer/filter in the report. |
| **Hidden KPI columns in fact table** | Base columns for CTR, CPC, CPA, ROAS, and profit are hidden because DAX measures dynamically and accurately recalculate these values based on filter context. |
| **Color formatting measures in separate folder** | The 12 conditional formatting measures are kept in a dedicated "Formatting" folder to keep the analytical measures list clean. |
| **Dedicated `_Medidas` table** | Centralizes all measures in an empty calculated table (`{ BLANK() }`), following industry best practices. |

### Conditional Formatting Pattern

Color formatting measures follow a consistent pattern:

```
Best performance   → #1D6FA5 (Blue)
Other values       → #5F6368 (Grey)
```

For gradient rankings (e.g., `Cor Investimento Plataforma`):

```
Rank 1 → #1D6FA5 (Blue)
Rank 2 → #40454B
Rank 3 → #5C6268
Rank 4 → #787E84
Rank 5 → #969BA0
Rank 6 → #B8BCC0 (Light Grey)
```

---

## 5. Metric Standardization Pattern

### Why Recalculate KPIs at Each Layer?

The original dataset already contains columns like CTR, CPC, CPA, ROAS, and profit. However, **all metrics are recalculated** across three checkpoints:

1. **Notebook 01 (Profiling)** — To validate if original values are correct.
2. **Notebook 02 (Bronze → Silver)** — To ensure consistency in the Silver layer.
3. **Semantic Model (DAX)** — To compute accurately within Power BI's filter context.

### The Problem with Averaging Ratios

If Power BI simply summed the `CTR` column from the fact table, the result would be the **sum of individual CTRs**, rather than the true aggregate CTR. A DAX measure solves this:

```dax
-- ❌ INCORRECT: Summing individual campaign CTRs
SUM(fact[CTR])

-- ✅ CORRECT: Recalculating dynamically based on volumes
DIVIDE(
    SUM(fact[clicks]),
    SUM(fact[impressions])
) * 100
```

---

## 6. Outlier Handling

### Decision: Preserve Outliers

Data profiling (nb_01) identified extreme values via the IQR method across metrics like ROAS, CPA, revenue, and profit. The decision was made **not to remove** these records. Justification:

> Inspection of the corresponding campaigns demonstrated that these values align with realistic relationships between investment, revenue, conversions, and volume. They represent campaigns with exceptionally high investment generating high returns (or vice versa), rather than data anomalies.

### When to Remove Outliers?

In future extensions of this project, removal would be justified if:

- Outliers were caused by **ingestion errors** (e.g., duplicate rows, wrong units).
- The goal was **predictive modeling** (Machine Learning), where outliers can skew algorithm training.
- The analysis required strict **confidence intervals**, where extreme values compromise interpretation.

---

## 7. Complete Architecture Diagram

```mermaid
flowchart TB
    subgraph SOURCE["Data Source"]
        CSV["tech_advertising_campaigns_dataset.csv\n10,000 records | 41 columns"]
    end

    subgraph PIPELINE["Pipeline: pl_ingest_marketing_campaigns"]
        direction TB
        NB01["nb_01 — Data Profiling\nExploratory analysis & validation"]
        NB02["nb_02 — Bronze to Silver\nSchema casting + recalculation + quality"]
        NB03["nb_03 — Silver to Gold\n7 summary analytical tables"]
        NB04["nb_04 — Star Schema\n1 fact + 8 dimensions"]
    end

    subgraph QUALITY["Quality"]
        NB05["nb_05 — Data Quality\nTesting Framework\nQuality Gate"]
    end

    subgraph LAKEHOUSE["Lakehouse: lh_marketing_analytics"]
        BRONZE["Files/bronze/raw/"]
        SILVER["Tables/silver_marketing_campaigns"]
        GOLD["Tables/gold_*"]
        STAR["Tables/fact_* + dim_*"]
    end

    subgraph SEMANTIC["Semantic Model"]
        SM["sm_marketing_analytics\nDirectLake | 28+ DAX measures"]
    end

    subgraph REPORT["Power BI Report"]
        PBI["Marketing Analytics\nBudget Optimization"]
    end

    CSV --> BRONZE
    BRONZE --> NB01
    NB01 --> NB02
    NB02 --> SILVER
    SILVER --> NB03
    NB03 --> GOLD
    GOLD --> NB04
    NB04 --> STAR
    STAR --> NB05
    STAR --> SM
    SM --> PBI

    style BRONZE fill:#CD7F32,color:#fff
    style SILVER fill:#C0C0C0,color:#000
    style GOLD fill:#FFD700,color:#000
    style STAR fill:#1D6FA5,color:#fff
```

![Complete Data Flow in Fabric](images/pipeline-fabric.jpg)
