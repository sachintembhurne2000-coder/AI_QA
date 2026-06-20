# AI QA Copilot — Default Knowledge Base Seed
# This file is auto-loaded into ChromaDB on first run if knowledge base is empty.
# Edit this file to add your organisation's specific standards.

QA_STANDARDS = """
=== QA ENGINEERING STANDARDS v1.0 ===

TEST CASE WRITING STANDARDS
============================
1. Every test case MUST have: unique ID, clear title, preconditions, numbered steps, expected result.
2. Title format: [Action] [Object] [Condition] — e.g., "Login with valid credentials succeeds"
3. Steps must be atomic — one action per step, no compound steps.
4. Expected results must be observable and measurable.
5. Preconditions must list ALL setup requirements.
6. Test data must be explicit — never "enter valid data", always specify exact values.

PRIORITY DEFINITIONS
=====================
- Critical: Core functionality without which the product cannot ship.
- High: Major feature that significantly impacts user experience.
- Medium: Standard feature or minor impact to user experience.
- Low: Cosmetic, edge case, or nice-to-have improvement.

BUG SEVERITY DEFINITIONS
=========================
- Critical: System crash, data loss, security breach, no workaround.
- High: Major feature broken, workaround exists but painful.
- Medium: Feature partially broken, acceptable workaround.
- Low: Cosmetic, typo, minor UX issue.

TEST TYPES
==========
- Functional: Verify feature works as specified.
- Negative: Verify system handles invalid input gracefully.
- Boundary: Test at exact boundaries (min, max, min-1, max+1).
- Security: Authentication, authorisation, injection, XSS.
- Performance: Response times, throughput, load behaviour.
- UI: Layout, visual consistency, accessibility.
- Integration: API contracts, inter-service communication.
- Regression: Previously-working functionality still works.

AUTOMATION BEST PRACTICES
==========================
1. Prefer data-testid > aria-label > id > CSS > XPath for locators.
2. Use Page Object Model — never put locators in test functions.
3. All tests must be independent — no shared mutable state.
4. Use fixtures for setup/teardown — not setUp/tearDown methods.
5. Parametrise tests for data-driven coverage.
6. Add retry logic only for truly flaky external dependencies.
7. Keep test files under 500 lines — split by feature.
8. All assertions must include a failure message.

API TESTING STANDARDS
=====================
1. Every endpoint requires: positive test, negative test (invalid auth), not-found test.
2. Verify: status code, response schema, response time (<500ms baseline).
3. Test idempotency for PUT/PATCH/DELETE operations.
4. Verify error response bodies (not just status codes).
5. Test pagination, filtering, and sorting where applicable.
6. Always clean up test data after each test run.

EMBEDDED TESTING STANDARDS
===========================
1. MQTT: Test all QoS levels (0, 1, 2). Verify message ordering for QoS 1+.
2. KNX: Validate group address ranges. Test ETS configuration on clean install.
3. BACnet: Verify COV subscriptions recover after network interruption.
4. Modbus: Test all used function codes. Verify exception code handling.
5. All device tests must include power-cycle recovery scenarios.
6. Test firmware OTA update path — both success and failure cases.

BUG REPORT STANDARDS
=====================
Bug reports must include:
1. Summary: One sentence describing the bug.
2. Steps to reproduce: Numbered, reproducible on a clean system.
3. Expected vs Actual: What should happen vs what actually happens.
4. Environment: OS, browser, app version, test environment.
5. Severity and Priority (separate concerns).
6. Logs/Screenshots: Attached or linked.
7. Root cause hypothesis (if known).
"""

REGRESSION_STRATEGY = """
=== REGRESSION TESTING STRATEGY ===

WHEN TO RUN REGRESSION
========================
- Every pull request to main/master
- Before every release candidate
- After every hotfix
- After infrastructure changes

REGRESSION SUITE TIERS
=======================
Tier 1 — Smoke (5-10 mins):
  - Login/authentication
  - Core navigation
  - Critical happy paths
  - Run on: every commit

Tier 2 — Sanity (20-30 mins):
  - All critical and high priority tests
  - Run on: PR merge to main

Tier 3 — Full Regression (2-4 hours):
  - All test cases
  - Run on: nightly or pre-release

IMPACT-BASED REGRESSION SELECTION
===================================
When code changes affect module X:
1. Run all tests tagged with module X.
2. Run all integration tests that involve module X's APIs.
3. Run Tier 1 smoke suite always.
4. Skip unrelated module tests if time-constrained.
"""
