"""
Bug Agent — generate structured bug reports from failure analysis
"""
import json
from services.llm import call_llm, extract_json

SYSTEM_PROMPT = """You are an expert QA engineer who writes clear, precise, and actionable bug reports.
Your reports follow industry best practices and contain all information a developer needs to reproduce and fix the issue.
Always respond with valid JSON only.
"""

BUG_REPORT_PROMPT = """Generate a complete, structured bug report based on the following information.

FAILURE ANALYSIS / ROOT CAUSE:
{failure_analysis}

ADDITIONAL CONTEXT:
- Test Case: {test_case}
- Environment: {environment}
- Tester Notes: {notes}

Respond as JSON:
{{
  "title": "Concise bug title (max 100 chars)",
  "bug_id": "BUG-001",
  "summary": "Clear 2-3 sentence description of the bug",
  "severity": "Critical | High | Medium | Low",
  "priority": "P1 | P2 | P3 | P4",
  "bug_type": "Functional | Performance | UI | Security | Integration | Configuration",
  "component": "Component or module affected",
  "environment": {{
    "os": "Operating System",
    "browser": "Browser and version (if applicable)",
    "app_version": "Application version",
    "test_environment": "Dev | QA | Staging | Production"
  }},
  "steps_to_reproduce": [
    "Step 1...",
    "Step 2..."
  ],
  "actual_result": "What actually happened",
  "expected_result": "What should have happened",
  "root_cause": "Technical root cause identified",
  "impact": "Business and technical impact of this bug",
  "logs_excerpt": "Relevant log snippet (max 500 chars)",
  "recommendations": [
    "Immediate fix recommendation",
    "Long-term improvement"
  ],
  "test_cases_affected": ["TC-001", "TC-002"],
  "suggested_labels": ["regression", "backend", "auth"],
  "estimated_fix_effort": "Hours | Days | Weeks"
}}
"""

FROM_LOG_ANALYSIS_PROMPT = """Convert this log analysis result into a complete bug report.

LOG ANALYSIS:
{log_analysis}

TEST CONTEXT: {context}

Generate the bug report as JSON with these fields:
title, bug_id, summary, severity, priority, bug_type, component,
environment (object), steps_to_reproduce (array), actual_result,
expected_result, root_cause, impact, logs_excerpt,
recommendations (array), suggested_labels (array), estimated_fix_effort
"""

JIRA_FORMAT_PROMPT = """Convert this bug report to Jira-compatible format.

BUG REPORT:
{bug_report}

Respond as JSON:
{{
  "summary": "Issue title",
  "description": "Full Jira description in wiki markup",
  "issuetype": {{"name": "Bug"}},
  "priority": {{"name": "P1 | P2 | P3 | P4"}},
  "labels": ["label1", "label2"],
  "components": [{{"name": "component"}}],
  "environment": "environment string",
  "customfield_story_points": 3
}}
"""


def generate_bug_report(
    failure_analysis: str,
    test_case: str = "Not specified",
    environment: str = "QA Environment",
    notes: str = "",
) -> dict:
    """Generate a structured bug report from failure analysis text."""
    prompt = BUG_REPORT_PROMPT.format(
        failure_analysis=failure_analysis[:5000],
        test_case=test_case,
        environment=environment,
        notes=notes,
    )
    raw = call_llm(SYSTEM_PROMPT, prompt, max_tokens=3000)
    return extract_json(raw)


def generate_from_log_analysis(log_analysis: dict, context: str = "") -> dict:
    """Generate bug report directly from log agent output."""
    prompt = FROM_LOG_ANALYSIS_PROMPT.format(
        log_analysis=json.dumps(log_analysis, indent=2)[:5000],
        context=context,
    )
    raw = call_llm(SYSTEM_PROMPT, prompt, max_tokens=3000)
    return extract_json(raw)


def format_for_jira(bug_report: dict) -> dict:
    """Format bug report for Jira REST API submission."""
    prompt = JIRA_FORMAT_PROMPT.format(
        bug_report=json.dumps(bug_report, indent=2)[:3000]
    )
    raw = call_llm(SYSTEM_PROMPT, prompt, max_tokens=1500)
    return extract_json(raw)


def severity_color(severity: str) -> str:
    colors = {
        "Critical": "#FF0000",
        "High": "#FF6B35",
        "Medium": "#F6AD55",
        "Low": "#68D391",
    }
    return colors.get(severity, "#A0AEC0")
