# Architecture

```mermaid
flowchart LR
    A[CSV Source] --> B[Raw file copy]
    B --> C[Bronze Parquet]
    C --> D[Silver Clean + Typed + DQ]
    D --> E[Gold Dimensions + Fact + Marts]
    E --> F[DuckDB Semantic Views]
    F --> G[Streamlit]
    H[Dagster] -. orchestrates + observes .-> B
    H -. orchestrates + observes .-> C
    H -. orchestrates + observes .-> D
    H -. orchestrates + observes .-> E
    H -. orchestrates + observes .-> F
```

Raw preserves the received physical file at `data/raw/servidores/servidores-2026.csv`. The inspected source contains two competencies (`202601`, `202602`), but Raw is intentionally not partitioned by `ano_mes`; partitioning or analytical organization can happen later in Bronze, Silver or Gold after the source has been preserved.

Dagster is not a data layer. It is the orchestrator that understands asset dependencies, executes materializations and exposes lineage/observability for the class demo.
