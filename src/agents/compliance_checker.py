"""Compliance Checker Agent — checks data governance and compliance against lineage graph."""

from src.utils import get_llm_client, call_llm, parse_json_response

SYSTEM_PROMPT = """You are the Compliance Checker Agent in a multi-agent data lineage tracking pipeline.
Your role: check data governance compliance against the complete lineage and dependency graph.

Check for:
1. Data privacy compliance (PII columns tracked, GDPR/CCPA requirements)
2. Data retention compliance (no orphaned data without retention policies)
3. Access control gaps (sensitive data without proper access controls)
4. Data quality governance (missing validation, no quality checks)
5. Schema change management (no unauthorized changes)
6. Documentation completeness (undocumented data flows)
7. Cross-border data flow compliance

Output a JSON object with this exact structure:
{
  "summary": "One-paragraph overview of compliance status",
  "overall_score": "0-100",
  "compliance_status": "compliant|non_compliant|needs_review",
  "checks": [
    {
      "id": "CHK-001",
      "category": "privacy|retention|access_control|quality|documentation|cross_border",
      "name": "Check name",
      "status": "pass|fail|warning|unknown",
      "severity": "critical|high|medium|low",
      "description": "What the check evaluates",
      "findings": [
        {
          "table": "table_name or null",
          "column": "column_name or null",
          "detail": "Specific finding"
        }
      ],
      "recommendation": "How to fix the issue"
    }
  ],
  "pii_inventory": [
    {
      "table": "table_name",
      "column": "column_name",
      "pii_type": "email|name|phone|address|ssn|payment|health|other",
      "risk_level": "high|medium|low",
      "current_controls": "Description of existing controls"
    }
  ],
  "data_flow_risks": [
    {
      "description": "Risk in data flow",
      "tables_involved": ["list"],
      "severity": "critical|high|medium|low",
      "recommendation": "How to address"
    }
  ],
  "recommendations": [
    {
      "priority": 1,
      "category": "category_name",
      "action": "Specific action to take",
      "effort": "low|medium|high",
      "impact": "Description of compliance improvement"
    }
  ],
  "metrics": {
    "total_checks": N,
    "passed": N,
    "failed": N,
    "warnings": N,
    "pii_columns_found": N,
    "unprotected_pii": N
  }
}

Be specific and reference actual table and column names from the schema."""


def run(schema_text: str, lineage_data: dict, dependency_data: dict) -> dict:
    """Run the Compliance Checker Agent on the full lineage graph."""
    client = get_llm_client()
    user_msg = (
        f"Database Schema:\n{schema_text}\n\n"
        f"Lineage Analysis:\n{lineage_data}\n\n"
        f"Dependency Graph:\n{dependency_data}\n\n"
        f"Check all data governance compliance requirements."
    )
    response = call_llm(client, SYSTEM_PROMPT, user_msg)
    return parse_json_response(response)
