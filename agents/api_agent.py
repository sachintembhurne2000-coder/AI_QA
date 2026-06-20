"""
API Agent — parse OpenAPI/Swagger specs and generate API test suites
"""
import json
import yaml
from services.llm import call_llm, extract_json

SYSTEM_PROMPT = """You are a senior API QA engineer expert in REST API testing,
OpenAPI/Swagger specifications, Pytest, and HTTPX.
Generate comprehensive, runnable API test suites.
"""

PARSE_SPEC_PROMPT = """Analyse this OpenAPI/Swagger specification and extract a summary of:
1. API title and base URL
2. Authentication method
3. List of endpoints (method, path, description, key parameters)
4. Response schemas

Respond as JSON:
{{
  "title": "...",
  "base_url": "...",
  "auth_type": "none | bearer | api_key | basic | oauth2",
  "endpoints": [
    {{
      "method": "GET|POST|PUT|DELETE|PATCH",
      "path": "/endpoint",
      "description": "...",
      "parameters": ["param1", "param2"],
      "request_body": "description or null",
      "responses": {{"200": "description", "400": "description"}}
    }}
  ]
}}

SPEC:
{spec_text}
"""

GENERATE_TESTS_PROMPT = """Generate a comprehensive Pytest + HTTPX API test suite from this OpenAPI spec.

API SUMMARY:
{api_summary}

SPEC (full):
{spec_text}

Generate complete test code with:
# === conftest.py ===
<base_url fixture, auth headers fixture, http client fixture>

# === tests/test_api_endpoints.py ===
<test class per endpoint group, positive + negative + boundary tests>

# === utils/api_helpers.py ===
<helper functions for assertions and data generation>

# === pytest.ini ===
<pytest configuration>

Coverage requirements:
- Happy path for each endpoint
- Missing required fields (400 validation)
- Invalid auth (401/403)
- Not found (404)
- At least one boundary value test per endpoint
"""

SUGGEST_TESTS_PROMPT = """Based on this API summary, suggest a comprehensive test strategy as JSON:
{{
  "test_cases": [
    {{
      "id": "API-001",
      "endpoint": "POST /users",
      "title": "Create user with valid data",
      "type": "Positive | Negative | Boundary | Security | Performance",
      "priority": "Critical | High | Medium | Low",
      "test_data": "Description of test data",
      "expected_status": 201,
      "expected_response": "Description of expected response",
      "assertions": ["assertion1", "assertion2"]
    }}
  ]
}}

API SUMMARY:
{api_summary}
"""


def parse_spec(spec_text: str) -> dict:
    """Parse OpenAPI spec text and return structured summary."""
    prompt = PARSE_SPEC_PROMPT.format(spec_text=spec_text[:8000])
    raw = call_llm(SYSTEM_PROMPT, prompt, max_tokens=2048)
    return extract_json(raw)


def generate_api_test_suite(spec_text: str, api_summary: dict) -> str:
    """Generate full Pytest + HTTPX test suite from spec."""
    prompt = GENERATE_TESTS_PROMPT.format(
        api_summary=json.dumps(api_summary, indent=2),
        spec_text=spec_text[:6000],
    )
    return call_llm(SYSTEM_PROMPT, prompt, max_tokens=4096)


def suggest_test_cases(api_summary: dict) -> list[dict]:
    """Generate structured test case list from API summary."""
    prompt = SUGGEST_TESTS_PROMPT.format(
        api_summary=json.dumps(api_summary, indent=2)
    )
    raw = call_llm(SYSTEM_PROMPT, prompt, max_tokens=3000)
    result = extract_json(raw)
    if isinstance(result, dict) and "test_cases" in result:
        return result["test_cases"]
    return result if isinstance(result, list) else []


def load_spec(text: str) -> dict:
    """Parse YAML or JSON OpenAPI spec string into a dict."""
    try:
        return yaml.safe_load(text)
    except Exception:
        pass
    try:
        return json.loads(text)
    except Exception:
        return {}
