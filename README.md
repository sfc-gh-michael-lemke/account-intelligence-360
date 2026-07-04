# Account Intelligence 360

> Natural language account intelligence powered by Snowflake Cortex Analyst.

A [Cortex Analyst](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst) semantic view for 360-degree account analysis at Snowflake.

## What It Does

Enables AEs and SDRs to query enriched account data in plain English — no SQL required. Combines Salesforce accounts with industry classification (7+ source consensus via MDM), employee count scoring, Crunchbase firmographic data, and SAI account priority scores into a single queryable semantic model.

## Business Value

| Use Case | Impact |
|----------|--------|
| Account segmentation | Filter accounts by industry, size, or SAI priority without SQL |
| ICP analysis | Identify ideal customer profile patterns across the book |
| Enrichment coverage audits | Which accounts are missing firmographic data? |
| Prospect prioritization | Surface high-SAI-score accounts for targeted outreach |

## Data Sources

| Source | Purpose |
|--------|---------|
| `MDM.MDM_INTERFACES.SFDC_ACCOUNT_CONSOLIDATED_INDUSTRY` | Consolidated Salesforce account + MDM-conformed industry classification |
| Crunchbase (via linkage) | Firmographic enrichment (employees, funding, HQ location) |
| SAI scoring | Snowflake account priority and health scores |
| 7+ industry classification sources | Consensus-scored industry/subindustry classification |

## Semantic Model

The `account_intelligence_360` semantic view exposes:

- **Dimensions**: Account name, industry, subindustry, theater, region, account type, SAI score
- **Facts**: Employee count (consensus-scored), enrichment coverage flags
- **Primary key**: `SOURCE_SYSTEM_ENTITY_ID`

## Deployment

Deploy via Cortex Code Desktop semantic view workflow, or directly in Snowsight:

```sql
-- See creation/ directory for full semantic view DDL
```

## Usage with Cortex Analyst

Once deployed, query in natural language:

> "Which HCLS accounts have more than 10,000 employees and a high SAI priority score?"
> "Show me all Financial Services accounts without approved industry classification"
> "What percentage of my accounts have Crunchbase data?"

## Value Realization

This semantic view is the foundation for AI-driven account intelligence at Snowflake. By making enriched, consensus-scored account data queryable in natural language, it eliminates the RevOps bottleneck of ad-hoc data requests and empowers the field team to self-serve account insights at scale — turning data engineering work into direct rep productivity.
