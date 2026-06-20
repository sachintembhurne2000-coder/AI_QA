"""
Automation Agent — generate Playwright, Selenium POM, and Pytest automation code
"""
from services.llm import call_llm

SYSTEM_PROMPT = """You are a senior test automation engineer expert in:
- Playwright (Python)
- Selenium WebDriver with Page Object Model (Python)
- Pytest with fixtures and conftest
- Clean, maintainable, well-commented code

Generate production-quality automation code. Always include imports.
"""

PLAYWRIGHT_PROMPT = """Generate complete Playwright Python automation code for these test cases.
Use pytest-playwright. Follow best practices: async/await, proper locators, explicit waits.

TEST CASES:
{test_cases_json}

Generate a complete test file with:
1. All imports
2. Fixtures in conftest.py section (mark clearly with # === conftest.py ===)
3. Page Object class(es) (mark with # === pages/your_page.py ===)
4. Test functions (mark with # === tests/test_your_feature.py ===)

Make the code runnable and complete.
"""

SELENIUM_PROMPT = """Generate complete Selenium Python + Pytest automation code using Page Object Model.

TEST CASES:
{test_cases_json}

Structure:
# === pages/base_page.py ===
<BasePage class>

# === pages/your_page.py ===
<Page Object class with locators as class attributes>

# === tests/conftest.py ===
<driver fixture, setup/teardown>

# === tests/test_your_feature.py ===
<Test class with test methods>

Use explicit waits (WebDriverWait). Include all imports.
"""

PYTEST_PROMPT = """Generate a comprehensive Pytest test suite (no browser automation) for API or unit testing.

TEST CASES:
{test_cases_json}

Include:
# === conftest.py ===
<shared fixtures>

# === tests/test_feature.py ===
<test functions with parametrize where appropriate>

# === utils/helpers.py ===
<helper functions>

Use pytest.mark, parametrize, and proper assertion messages.
"""

API_CODE_PROMPT = """Generate a complete Pytest + HTTPX API test suite for these test cases.

BASE URL: {base_url}
TEST CASES:
{test_cases_json}

Include:
# === conftest.py ===
<client fixture, auth fixture>

# === tests/test_api.py ===
<API test functions with proper assertions on status codes, response body, headers>

# === utils/api_client.py ===
<reusable API client wrapper>

Follow AAA pattern (Arrange-Act-Assert). Cover happy paths and error cases.
"""


def _import_json(test_cases: list[dict]) -> str:
    import json
    return json.dumps(test_cases, indent=2)


def generate_playwright(test_cases: list[dict]) -> str:
    prompt = PLAYWRIGHT_PROMPT.format(test_cases_json=_import_json(test_cases))
    return call_llm(SYSTEM_PROMPT, prompt, max_tokens=4096)


def generate_selenium(test_cases: list[dict]) -> str:
    prompt = SELENIUM_PROMPT.format(test_cases_json=_import_json(test_cases))
    return call_llm(SYSTEM_PROMPT, prompt, max_tokens=4096)


def generate_pytest(test_cases: list[dict]) -> str:
    prompt = PYTEST_PROMPT.format(test_cases_json=_import_json(test_cases))
    return call_llm(SYSTEM_PROMPT, prompt, max_tokens=4096)


def generate_api_tests(test_cases: list[dict], base_url: str = "https://api.example.com") -> str:
    prompt = API_CODE_PROMPT.format(
        test_cases_json=_import_json(test_cases),
        base_url=base_url,
    )
    return call_llm(SYSTEM_PROMPT, prompt, max_tokens=4096)


def parse_code_sections(raw_code: str) -> dict[str, str]:
    """
    Parse generated code into sections based on # === filename === markers.
    Returns dict of {filename: code}.
    """
    import re
    sections = {}
    pattern = r"#\s*===\s*(.+?)\s*===\s*\n"
    parts = re.split(pattern, raw_code)

    if len(parts) == 1:
        # No sections — return as single file
        return {"automation_code.py": raw_code.strip()}

    # parts[0] is pre-first-section content (usually empty)
    # parts[1::2] are filenames, parts[2::2] are code blocks
    filenames = parts[1::2]
    codes = parts[2::2]

    for filename, code in zip(filenames, codes):
        filename = filename.strip()
        sections[filename] = code.strip()

    return sections
