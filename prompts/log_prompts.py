# Log Analysis Prompt Templates
# These are loaded by agents/log_agent.py
# Edit these to add organisation-specific log patterns

EMBEDDED_CONTEXT = """
When analysing embedded device logs, pay special attention to:

MQTT:
- Connection refused (return codes 1-5)
- Unexpected disconnects (RC=0 vs RC=1)
- QoS delivery failures
- Retained message anomalies
- Topic permission errors

KNX:
- Telegram errors (checksum, address)
- Group object communication failures
- ETS configuration mismatches
- KNX/IP router timeouts

BACnet:
- APDU timeout and retry exhaustion
- Confirmed service errors
- Device offline (IAm not received)
- COV subscription failures
- WhoIs broadcast storms

Modbus:
- Exception codes: 01 (illegal function), 02 (illegal address),
  03 (illegal data value), 04 (slave device failure)
- Timeout and framing errors
- CRC mismatches
- Slave ID conflicts

Gateway/Firmware:
- Watchdog resets
- Memory allocation failures
- Stack overflow indicators
- Boot loop patterns
- Firmware version mismatches
"""

PYTEST_LOG_HINTS = """
When analysing Pytest logs, identify:
- FAILED vs ERROR vs WARNING distinctions
- Fixture setup/teardown failures
- Parametrize failures (which parameter set failed)
- Import errors (missing dependencies)
- Assertion errors (exact values compared)
- Timeout warnings
- Flaky test indicators (intermittent failures)
"""

CI_LOG_HINTS = """
When analysing CI/CD logs (Jenkins, GitHub Actions, GitLab CI):
- Build stage vs test stage vs deploy stage failures
- Environment variable missing errors
- Docker/container startup failures
- Network connectivity issues in CI environment
- Resource exhaustion (OOM, disk full)
- Dependency resolution failures
- Test parallelisation conflicts
"""
