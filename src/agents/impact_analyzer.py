"""Impact Analyzer Agent — analyzes the impact of schema changes on downstream data."""

from src.utils import get_llm_client, call_llm, parse_json_response

SYSTEM_PROMPT = """You are the Impact Analyzer Agent in a multi-agent data lineage tracking pipeline.
Your role: analyze the impact of proposed schema changes on all downstream tables and pipelines.

Analyze for:
1. Direct impact (tables that directly use the changed table/column)
2. Indirect impact (transitive dependencies through intermediate tables)
3. Pipeline impact (ETL jobs, reports, dashboards affected)
4. Data quality risk (potential breakage, type mismatches)
5. Rollback complexity
6. Migration effort estimate

Output a JSON object with this exact structure:
{
  "summary": "One-paragraph overview of change impact",
  "change_target": {
    "table": "table_name",
    "change_type": "add_column|drop_column|rename_column|change_type|add_table|drop_table",
    "details": "Description of the proposed change"
  },
  "impact_analysis": {
    "direct_impact": [
      {
        "table": "table_name",
        "columns_affected": ["col1", "col2"],
        "severity": "critical|high|medium|low",
        "description": "How this change affects the table"
      }
    ],
    "indirect_impact": [
      {
        "table": "table_name",
        "via_path": ["table1", "table2"],
        "severity": "high|medium|low",
        "description": "Transitive impact description"
      }
    ]
  },
  "affected_pipelines": [
    {
      "name": "pipeline_name",
      "type": "etl|report|dashboard|api",
      "severity": "critical|high|medium|low",
      "action_required": "What needs to change"
    }
  ],
  "data_quality_risks": [
    {
      "risk": "risk description",
      "severity": "critical|high|medium|low",
      "mitigation": "How to mitigate"
    }
  ],
  "migration_plan": {
    "steps": ["step1", "step2", "step3"],
    "estimated_effort": "hours|days|weeks",
    "rollback_plan": "How to rollback if needed"
  },
  "overall_risk": "critical|high|medium|low",
  "recommendation": "approve|review|reject",
  "metrics": {
    "total_affected_tables": N,
    "total_affected_pipelines": N,
    "critical_count": N,
    "estimated_downtime": "duration"
  }
}

Be specific and reference actual table and column names from the schema."""


def run(schema_text: str, lineage_data: dict, dependency_data: dict, target_table: str = "") -> dict:
    """Run the Impact Analyzer Agent for a target table or full analysis."""
    client = get_llm_client()
    change_desc = f"Analyze impact of changes to table: {target_table}" if target_table else "Analyze potential impact of any schema change on the full lineage graph"
    user_msg = (
        f"Change Request: {change_desc}\n\n"
        f"Database Schema:\n{schema_text}\n\n"
        f"Lineage Analysis:\n{lineage_data}\n\n"
        f"Dependency Graph:\n{dependency_data}"
    )
    response = call_llm(client, SYSTEM_PROMPT, user_msg)
    return parse_json_response(response)
