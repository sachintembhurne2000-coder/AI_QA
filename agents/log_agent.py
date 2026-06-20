"""
Log Agent — AI-powered root cause analysis for test, server, and embedded device logs
"""
from services.llm import call_llm, extract_json
from services.parser import truncate_for_llm

SYSTEM_PROMPT = """You are an expert QA engineer and DevOps specialist with deep knowledge of:
- Pytest and test framework logs
- Jenkins CI/CD logs
- Browser console logs (Chrome DevTools)
- Application server logs (Django, FastAPI, Node.js)
- REST API logs
- Embedded device protocols: MQTT, KNX, BACnet, Modbus, gateway logs
- Firmware crash dumps and stack traces

Analyse logs carefully and provide precise, actionable root cause analysis.
"""

ANALYSE_PROMPT = """Analyse the following log file(s) and identify:
1. All errors, warnings, and anomalies
2. Root causes with confidence levels
3. Timeline of events leading to failure
4. Specific line references
5. Recommended fixes

LOG TYPE: {log_type}

LOGS:
{log_content}

Respond as JSON:
{{
  "overall_status": "PASS | FAIL | WARNING",
  "summary": "2-3 sentence summary of what happened",
  "errors_found": [
    {{
      "severity": "CRITICAL | HIGH | MEDIUM | LOW",
      "message": "Error message or pattern",
      "line_reference": "Line number or timestamp if available",
      "frequency": "How many times this occurred"
    }}
  ],
  "root_causes": [
    {{
      "rank": 1,
      "confidence": "High | Medium | Low",
      "cause": "Root cause description",
      "evidence": "Specific log lines or patterns supporting this",
      "category": "Network | Configuration | Code | Environment | Timeout | Authentication | Protocol | Hardware"
    }}
  ],
  "timeline": [
    {{
      "timestamp": "time or sequence number",
      "event": "What happened"
    }}
  ],
  "recommendations": [
    {{
      "priority": "Immediate | Short-term | Long-term",
      "action": "Specific action to take",
      "expected_outcome": "What this will fix"
    }}
  ],
  "embedded_protocol_issues": {{
    "mqtt": [],
    "knx": [],
    "bacnet": [],
    "modbus": []
  }}
}}
"""

COMPARE_PROMPT = """Compare these two log sets — a PASSING run and a FAILING run.
Identify exactly what changed or went wrong.

PASSING LOG:
{passing_log}

FAILING LOG:
{failing_log}

Respond as JSON:
{{
  "diff_summary": "Key differences between passing and failing runs",
  "failure_trigger": "The specific event or condition that caused the failure",
  "differences": [
    {{
      "category": "what differs",
      "in_passing": "value/event in passing run",
      "in_failing": "value/event in failing run"
    }}
  ],
  "root_cause": "Primary root cause of the failure",
  "fix": "Recommended fix"
}}
"""

SELF_HEAL_PROMPT = """The following test failed because UI elements changed.
Analyse the error and suggest self-healing locator updates.

FAILED TEST LOG:
{error_log}

CURRENT LOCATORS (if available):
{current_locators}

Respond as JSON:
{{
  "broken_locators": [
    {{
      "original": "original locator that broke",
      "reason": "why it broke",
      "suggestions": [
        {{
          "locator": "new locator",
          "type": "css | xpath | id | text | role",
          "confidence": "High | Medium | Low",
          "rationale": "why this is better"
        }}
      ]
    }}
  ],
  "test_recommendations": ["recommendation 1", "recommendation 2"]
}}
"""

LOG_TYPES = [
    "Auto-detect",
    "Pytest / Test Framework",
    "Jenkins / CI-CD",
    "Browser Console",
    "Application Server",
    "REST API",
    "MQTT (Embedded)",
    "KNX (Building Automation)",
    "BACnet (Building Automation)",
    "Modbus (Industrial)",
    "Gateway / Firmware",
    "Mixed / Multiple",
]


def analyse_logs(log_content: str, log_type: str = "Auto-detect") -> dict:
    """Run AI root cause analysis on log content."""
    truncated = truncate_for_llm(log_content, max_chars=50_000)
    prompt = ANALYSE_PROMPT.format(log_type=log_type, log_content=truncated)
    raw = call_llm(SYSTEM_PROMPT, prompt, max_tokens=4096)
    return extract_json(raw)


def compare_logs(passing_log: str, failing_log: str) -> dict:
    """Compare a passing and failing log to find the diff."""
    prompt = COMPARE_PROMPT.format(
        passing_log=truncate_for_llm(passing_log, 20_000),
        failing_log=truncate_for_llm(failing_log, 20_000),
    )
    raw = call_llm(SYSTEM_PROMPT, prompt, max_tokens=2048)
    return extract_json(raw)


def suggest_self_healing(error_log: str, current_locators: str = "") -> dict:
    """Suggest self-healing locator updates from a failed test log."""
    prompt = SELF_HEAL_PROMPT.format(
        error_log=truncate_for_llm(error_log, 10_000),
        current_locators=current_locators or "Not provided",
    )
    raw = call_llm(SYSTEM_PROMPT, prompt, max_tokens=2048)
    return extract_json(raw)
