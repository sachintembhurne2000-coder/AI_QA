"""
Requirement Agent — extract structured requirements and generate test cases
"""
from services.llm import call_llm, extract_json
from services.rag import build_context

SYSTEM_PROMPT = """You are a senior QA engineer and requirements analyst.
Your job is to analyse software requirements documents and generate comprehensive,
structured test cases in JSON format.

Always respond with ONLY valid JSON — no preamble, no markdown fences outside JSON.
"""

EXTRACT_PROMPT = """Analyse the following requirements document and extract:
1. A brief summary (2-3 sentences)
2. Key functional requirements list
3. Actors / users
4. Acceptance criteria
5. Edge cases to consider

Respond as JSON:
{{
  "summary": "...",
  "functional_requirements": ["req1", "req2", ...],
  "actors": ["actor1", ...],
  "acceptance_criteria": ["criteria1", ...],
  "edge_cases": ["edge1", ...]
}}

REQUIREMENTS DOCUMENT:
{doc_text}
"""

TEST_CASES_PROMPT = """Based on these requirements, generate {max_cases} comprehensive test cases.
Cover: positive paths, negative paths, boundary values, edge cases, and security basics.

{rag_context}

REQUIREMENTS:
{requirements}

Respond ONLY with a JSON array:
[
  {{
    "id": "TC-001",
    "title": "Short descriptive title",
    "type": "Functional | Negative | Boundary | Security | UI | Performance",
    "priority": "Critical | High | Medium | Low",
    "preconditions": "What must be true before the test",
    "steps": ["Step 1", "Step 2", "Step 3"],
    "expected_result": "What should happen",
    "tags": ["login", "auth"]
  }}
]
"""


def extract_requirements(doc_text: str) -> dict:
    """Parse a requirements document and return structured extraction."""
    prompt = EXTRACT_PROMPT.format(doc_text=doc_text[:12000])
    raw = call_llm(SYSTEM_PROMPT, prompt, max_tokens=2048)
    return extract_json(raw)


def generate_test_cases(requirements_text: str, max_cases: int = 20,
                        use_rag: bool = True) -> list[dict]:
    """
    Generate structured test cases from requirements text.
    Optionally enriches with RAG context.
    """
    rag_ctx = ""
    if use_rag:
        ctx = build_context(requirements_text[:500], n_results=3)
        if ctx:
            rag_ctx = f"RELEVANT KNOWLEDGE BASE CONTEXT:\n{ctx}\n"

    prompt = TEST_CASES_PROMPT.format(
        max_cases=max_cases,
        rag_context=rag_ctx,
        requirements=requirements_text[:10000],
    )
    raw = call_llm(SYSTEM_PROMPT, prompt, max_tokens=4096)
    result = extract_json(raw)

    # Normalise — ensure it's a list
    if isinstance(result, dict) and "test_cases" in result:
        result = result["test_cases"]
    if not isinstance(result, list):
        raise ValueError("LLM did not return a list of test cases")

    # Ensure IDs
    for i, tc in enumerate(result):
        if "id" not in tc or not tc["id"]:
            tc["id"] = f"TC-{i+1:03d}"

    return result
