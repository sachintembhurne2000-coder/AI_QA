"""
Session State Manager — helpers for Streamlit session state management
"""
import streamlit as st
from datetime import datetime


def init_session():
    """Initialise all required session state keys with defaults."""
    defaults = {
        "test_cases": [],
        "req_analysis": None,
        "generated_code": {},
        "raw_code": "",
        "api_summary": None,
        "api_test_cases": [],
        "api_code": "",
        "log_analysis": None,
        "log_diff": None,
        "heal_result": None,
        "screenshot_analysis": None,
        "bug_report": None,
        "jira_payload": None,
        "bug_from_log": None,
        "bug_from_screenshot": None,
        "tc_for_automation": None,
        "history": [],           # list of history entries
        "llm_provider": "Claude (Anthropic)",
        "api_key": "",
        "model": "claude-sonnet-4-6",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def push_history(action: str, summary: str, data: dict = None):
    """Append an action to the session history log."""
    entry = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "action": action,
        "summary": summary,
        "data": data or {},
    }
    if "history" not in st.session_state:
        st.session_state["history"] = []
    st.session_state["history"].insert(0, entry)  # newest first
    # Keep last 50 entries
    st.session_state["history"] = st.session_state["history"][:50]


def get_history() -> list:
    return st.session_state.get("history", [])


def clear_tool_state(tool: str):
    """Clear state for a specific tool to start fresh."""
    tool_keys = {
        "test_cases": ["test_cases", "req_analysis"],
        "automation": ["generated_code", "raw_code", "tc_for_automation"],
        "api": ["api_summary", "api_test_cases", "api_code"],
        "log": ["log_analysis", "log_diff", "heal_result", "bug_from_log"],
        "screenshot": ["screenshot_analysis", "bug_from_screenshot"],
        "bug": ["bug_report", "jira_payload"],
    }
    keys = tool_keys.get(tool, [])
    for k in keys:
        if k in st.session_state:
            del st.session_state[k]


def has_api_key() -> bool:
    """Check whether a valid API key is configured."""
    provider = st.session_state.get("llm_provider", "")
    if "Ollama" in provider:
        return True
    return bool(st.session_state.get("api_key", "").strip())


def api_key_warning():
    """Display a standardised warning if no API key is set."""
    if not has_api_key():
        st.warning("⚠️ No API key configured. Please enter your API key in the sidebar.")
        return True
    return False
