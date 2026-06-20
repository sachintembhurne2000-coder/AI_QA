"""Log Analyser page"""
import streamlit as st
import json
import pandas as pd
from agents.log_agent import analyse_logs, compare_logs, suggest_self_healing, LOG_TYPES
from services.parser import parse_document
from services.export import to_json_bytes


def _severity_badge(s):
    colors = {"CRITICAL": "#FF0000", "HIGH": "#FF6B35", "MEDIUM": "#F6AD55", "LOW": "#68D391"}
    c = colors.get(s.upper(), "#A0AEC0")
    return f'<span style="background:{c};color:white;padding:2px 8px;border-radius:10px;font-size:0.8rem;font-weight:bold;">{s}</span>'


def _confidence_icon(c):
    return {"High": "🟢", "Medium": "🟡", "Low": "🔴"}.get(c, "⚪")


def render():
    st.markdown("""
    <div class="main-header">
        <h1>🔍 Log Analyser</h1>
        <p>Upload test, server, or embedded device logs → AI identifies root causes with confidence scores</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Mode tabs ─────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["🔍 Single Log Analysis", "⚖️ Compare Pass vs Fail", "🔧 Self-Healing Locators"])

    # ── Tab 1: Single log ─────────────────────────────────────────────────────
    with tab1:
        col1, col2 = st.columns([2, 1])
        with col1:
            uploaded = st.file_uploader(
                "Upload log file",
                type=["log", "txt", "json", "xml", "csv"],
                key="single_log",
            )
        with col2:
            log_type = st.selectbox("Log Type", LOG_TYPES)

        pasted_log = st.text_area(
            "— or paste log content —",
            height=200,
            placeholder="Paste log content here...",
            key="pasted_single",
        )

        log_text = ""
        if uploaded:
            log_text = uploaded.read().decode("utf-8", errors="replace")
            st.success(f"✅ Loaded: **{uploaded.name}** ({len(log_text):,} chars)")
        elif pasted_log.strip():
            log_text = pasted_log.strip()

        analyse_btn = st.button("🔍 Analyse Log", type="primary", key="analyse_single")

        if analyse_btn:
            if not log_text:
                st.warning("Please upload or paste a log file.")
                return
            if not st.session_state.get("api_key") and st.session_state.get("llm_provider") != "Ollama (Local)":
                st.error("Please configure your API key in the sidebar.")
                return

            with st.spinner("🧠 Analysing log... (15-30 seconds)"):
                try:
                    result = analyse_logs(log_text, log_type)
                    st.session_state["log_analysis"] = result
                    st.session_state["log_text_raw"] = log_text
                except Exception as e:
                    st.error(f"Analysis error: {e}")
                    return

        if "log_analysis" in st.session_state:
            result = st.session_state["log_analysis"]
            _display_analysis(result)

    # ── Tab 2: Compare ────────────────────────────────────────────────────────
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**✅ Passing Run Log**")
            pass_file = st.file_uploader("Upload passing log", type=["log", "txt"], key="pass_log")
            pass_text_area = st.text_area("or paste passing log", height=150, key="pass_paste")

        with col2:
            st.markdown("**❌ Failing Run Log**")
            fail_file = st.file_uploader("Upload failing log", type=["log", "txt"], key="fail_log")
            fail_text_area = st.text_area("or paste failing log", height=150, key="fail_paste")

        compare_btn = st.button("⚖️ Compare Logs", type="primary", key="compare_btn")

        if compare_btn:
            passing = (pass_file.read().decode("utf-8", errors="replace") if pass_file else pass_text_area).strip()
            failing = (fail_file.read().decode("utf-8", errors="replace") if fail_file else fail_text_area).strip()

            if not passing or not failing:
                st.warning("Please provide both passing and failing logs.")
            else:
                with st.spinner("⚖️ Comparing logs..."):
                    try:
                        diff = compare_logs(passing, failing)
                        st.session_state["log_diff"] = diff
                    except Exception as e:
                        st.error(f"Comparison error: {e}")

        if "log_diff" in st.session_state:
            diff = st.session_state["log_diff"]
            st.markdown("---")
            st.subheader("📊 Comparison Result")
            st.info(f"**Diff Summary:** {diff.get('diff_summary', '')}")
            st.error(f"**Failure Trigger:** {diff.get('failure_trigger', '')}")
            st.success(f"**Recommended Fix:** {diff.get('fix', '')}")

            if diff.get("differences"):
                df = pd.DataFrame(diff["differences"])
                st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Tab 3: Self-healing ───────────────────────────────────────────────────
    with tab3:
        st.markdown("Paste error log from a failed test where UI locators broke.")
        error_log = st.text_area("Failed test error log", height=200, key="heal_log")
        current_locators = st.text_area(
            "Current locators (optional)",
            height=100,
            placeholder='By.ID("submit-btn"), By.CSS_SELECTOR(".login-form input[name=username]")',
            key="heal_locators",
        )

        heal_btn = st.button("🔧 Suggest Self-Healing Updates", type="primary")

        if heal_btn and error_log:
            with st.spinner("🔧 Analysing broken locators..."):
                try:
                    result = suggest_self_healing(error_log, current_locators)
                    st.session_state["heal_result"] = result
                except Exception as e:
                    st.error(f"Error: {e}")

        if "heal_result" in st.session_state:
            hr = st.session_state["heal_result"]
            st.markdown("---")
            st.subheader("🔧 Self-Healing Suggestions")

            for bl in hr.get("broken_locators", []):
                with st.expander(f"🔴 {bl.get('original', 'Unknown locator')} — {bl.get('reason', '')}"):
                    for s in bl.get("suggestions", []):
                        conf_icon = _confidence_icon(s.get("confidence", ""))
                        st.markdown(f"{conf_icon} **{s.get('type', '')}:** `{s.get('locator', '')}`")
                        st.caption(s.get("rationale", ""))

            if hr.get("test_recommendations"):
                st.markdown("**📝 Recommendations:**")
                for r in hr["test_recommendations"]:
                    st.markdown(f"- {r}")


def _display_analysis(result: dict):
    st.markdown("---")
    st.subheader("📊 Analysis Results")

    # Status
    status = result.get("overall_status", "UNKNOWN")
    status_color = {"PASS": "success", "FAIL": "error", "WARNING": "warning"}.get(status, "info")
    getattr(st, status_color)(f"**Overall Status: {status}** — {result.get('summary', '')}")

    col1, col2 = st.columns(2)

    # Errors
    with col1:
        st.subheader("🚨 Errors Found")
        errors = result.get("errors_found", [])
        if errors:
            for err in errors:
                sev = err.get("severity", "LOW")
                st.markdown(
                    f"{_severity_badge(sev)} **{err.get('message', '')}** "
                    f"(×{err.get('frequency', 1)})",
                    unsafe_allow_html=True,
                )
                if err.get("line_reference"):
                    st.caption(f"📍 {err['line_reference']}")
        else:
            st.info("No explicit errors detected.")

    # Root causes
    with col2:
        st.subheader("🎯 Root Causes")
        for rc in result.get("root_causes", []):
            ci = _confidence_icon(rc.get("confidence", ""))
            with st.expander(f"#{rc.get('rank', '?')} {ci} {rc.get('cause', '')[:60]}..."):
                st.markdown(f"**Confidence:** {rc.get('confidence', '')}")
                st.markdown(f"**Category:** {rc.get('category', '')}")
                st.markdown(f"**Evidence:**")
                st.code(rc.get("evidence", ""), language="text")

    # Timeline
    timeline = result.get("timeline", [])
    if timeline:
        st.subheader("⏱️ Event Timeline")
        df = pd.DataFrame(timeline)
        st.dataframe(df, use_container_width=True, hide_index=True)

    # Recommendations
    recs = result.get("recommendations", [])
    if recs:
        st.subheader("💡 Recommendations")
        for r in recs:
            icon = {"Immediate": "🔴", "Short-term": "🟡", "Long-term": "🟢"}.get(r.get("priority", ""), "⚪")
            st.markdown(f"{icon} **[{r.get('priority')}]** {r.get('action', '')} → _{r.get('expected_outcome', '')}_")

    # Embedded protocol issues
    ep = result.get("embedded_protocol_issues", {})
    if any(ep.values()):
        st.subheader("📡 Embedded Protocol Issues")
        for proto, issues in ep.items():
            if issues:
                st.markdown(f"**{proto.upper()}:**")
                for issue in issues:
                    st.markdown(f"- {issue}")

    # Export
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📋 Export Analysis (JSON)",
            data=to_json_bytes(result),
            file_name="log_analysis.json",
            mime="application/json",
            use_container_width=True,
        )
    with col2:
        if st.button("🐛 Generate Bug Report", use_container_width=True):
            st.session_state["bug_from_log"] = result
            st.success("Analysis stored! Navigate to 🐛 Bug Report Generator")
