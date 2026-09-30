# Technical Documentation Hub

> Reference portal and implementation guides for the **Marketing Budget Optimization** platform on Microsoft Fabric.

[Português](README.md) | [English](README.en.md)

---

## Overview

This directory contains in-depth documentation covering data engineering, analytical modeling, and business logic across the entire solution. Whether you are a reviewer, data engineer, analytics engineer, or technical lead, use the guides below to explore implementation details.

---

## Documentation Index

| Guide | Description | Available Languages |
|:---|:---|:---:|
| [Architecture Guide](architecture.en.md) | Technical decisions, Medallion Architecture (Bronze/Silver/Gold), data flow, and architecture diagrams | [PT](architecture.md) \| [EN](architecture.en.md) |
| [Data Dictionary](data-dictionary.en.md) | Full specification of all 41 raw features, Delta tables (Silver/Gold), Star Schema, and metrics catalog | [PT](data-dictionary.md) \| [EN](data-dictionary.en.md) |
| [Notebooks Guide](notebooks-guide.en.md) | Step-by-step walkthrough for notebooks (nb_01 through nb_05), validation rules, idempotency, and Quality Gate | [PT](notebooks-guide.md) \| [EN](notebooks-guide.en.md) |
| [Semantic Model & Power BI Guide](semantic-model-guide.en.md) | DirectLake connectivity, 28+ DAX measures catalog, TMDL code conventions, and conditional formatting | [PT](semantic-model-guide.md) \| [EN](semantic-model-guide.en.md) |

---

## Recommended Reading Path

Depending on your background and focus, we suggest following these reading paths:

### For Technical Reviewers and Tech Leads
1. [Architecture Guide](architecture.en.md): Understand the core design principles, trade-offs, and Medallion + DirectLake topology.
2. [Semantic Model Guide](semantic-model-guide.en.md): Review TMDL code structure, dimensional modeling, and enterprise DAX standards.
3. [Notebooks Guide](notebooks-guide.en.md) (nb_05 Section): Examine the automated Data Quality framework and audit Quality Gate.

### For Data Engineers and Analytics Engineers
1. [Notebooks Guide](notebooks-guide.en.md): Learn how PySpark cleans, enriches, and transforms data across each layer.
2. [Data Dictionary](data-dictionary.en.md): Inspect schema definitions, surrogate keys, and referential integrity relationships.
3. [Architecture Guide](architecture.en.md): Understand how data moves across OneLake and Delta tables.

---

[Back to Main Repository](../README.en.md)
