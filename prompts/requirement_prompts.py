# Requirement Agent Prompt Templates
# These are loaded by agents/requirement_agent.py
# Edit these to tune AI behaviour for your organisation's standards

SYSTEM = """You are a senior QA engineer and requirements analyst with 15+ years of experience.
Your expertise spans web applications, embedded systems, IoT, building automation (KNX, BACnet),
and industrial protocols (MQTT, Modbus).

When analysing requirements, you:
- Identify both explicit and implicit requirements
- Flag ambiguities that could affect testability
- Apply equivalence partitioning and boundary value analysis
- Consider all actors, positive/negative flows, and edge cases
- Follow IEEE 829 test documentation standards

Always respond with ONLY valid JSON — no preamble, no markdown fences.
"""

EXTRACT = """Analyse the following requirements document and extract structured information.

Respond as JSON:
{{
  "summary": "2-3 sentence overview of the system/feature",
  "functional_requirements": [
    "FR-001: System shall...",
    "FR-002: System shall..."
  ],
  "non_functional_requirements": [
    "Performance: ...",
    "Security: ..."
  ],
  "actors": ["Actor 1", "Actor 2"],
  "acceptance_criteria": [
    "Given ... When ... Then ..."
  ],
  "edge_cases": [
    "What if the user...",
    "What happens when..."
  ],
  "ambiguities": [
    "Requirement X is unclear because..."
  ],
  "testability_score": 85,
  "testability_notes": "Overall assessment of how testable these requirements are"
}}

REQUIREMENTS DOCUMENT:
{doc_text}
"""

GENERATE_TEST_CASES = """Generate {max_cases} comprehensive test cases from the requirements below.

Coverage requirements:
- Positive/happy path tests
- Negative tests (invalid inputs, error conditions)
- Boundary value tests
- Edge cases
- Security basics (if applicable)
- Integration points

{rag_context}

REQUIREMENTS:
{requirements}

Respond ONLY with a JSON array. Each test case:
{{
  "id": "TC-001",
  "title": "Concise, action-oriented title",
  "module": "Feature or module name",
  "type": "Functional | Negative | Boundary | Security | UI | Performance | Integration",
  "priority": "Critical | High | Medium | Low",
  "preconditions": "State of system before test",
  "test_data": "Specific data values to use",
  "steps": [
    "Navigate to...",
    "Enter... in the... field",
    "Click..."
  ],
  "expected_result": "Precise, observable outcome",
  "traceability": "FR-001",
  "tags": ["tag1", "tag2"],
  "estimated_duration_mins": 5
}}
"""
