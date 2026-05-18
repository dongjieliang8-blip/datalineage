"""Lineage Scanner Agent — scans data sources and extracts data lineage information."""

from src.utils import get_llm_client, call_llm, parse_json_response

SYSTEM_PROMPT = """You are the Lineage Scanner Agent in a multi-agent data lineage tracking pipeline.
Your role: scan the provided database schema and extract all data lineage information.

Analyze for:
1. Source tables (raw data ingestion points)
2. Derived/transformed tables (created from other tables via views, CTAs, ETL)
3. Column-level lineage (which source columns feed into which target columns)
4. Transformations applied (aggregation, join, filter, cast, lookup)
5. Data flow direction (upstream vs downstream)

Output a JSON object with this exact structure:
{
  "summary": "One-paragraph overview of data lineage landscape",
  "total_tables": N,
  "source_tables": N,
  "derived_tables": N,
  "lineage_edges": [
    {
      "source_table": "table_name",
      "source_columns": ["col1", "col2"],
      "target_table": "table_name",
      "target_columns": ["col1", "col2"],
      "transformation": "join|aggregate|filter|cast|lookup|direct",
      "description": "How data flows from source to target"
    }
  ],
  "tables": [
    {
      "name": "table_name",
      "type": "source|derived|unknown",
      "columns": [
        {
          "name": "column_name",
          "type": "data_type",
          "is_computed": true/false,
          "upstream_sources": [{"table": "...", "column": "..."}]
        }
      ],
      "description": "What this table contains"
    }
  ],
  "transformations": [
    {
      "name": "transform_1",
      "type": "join|aggregate|filter|cast|lookup",
      "input_tables": ["table1", "table2"],
      "output_table": "table3",
      "description": "What the transformation does"
    }
  ],
  "metrics": {
    "total_edges": N,
    "max_chain_depth": N,
    "orphan_columns": N,
    "untracked_sources": N
  }
}

Be specific and reference actual table and column names from the schema."""


def run(schema_text: str) -> dict:
    """Run the Lineage Scanner Agent on a schema definition."""
    client = get_llm_client()
    user_msg = f"Database Schema:\n\n{schema_text}"
    response = call_llm(client, SYSTEM_PROMPT, user_msg)
    return parse_json_response(response)
