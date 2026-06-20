"""Bug Report Generator page"""
import streamlit as st
import json
from agents.bug_agent import generate_bug_report, generate_from_log_analysis, format_for_jira, severity_color
from services.export import bug_report_to_word, to_json_bytes


def _sev_badge(sev: str):
    c = severity_color(sev)
    return f'<span style="background:{c};color:white;padding:3px 10px;border-radius:12px;font-size:0.85rem;font-weight:bold;">{sev}</span>'


def render():
    st.markdown("""
    <div class="main-header">
        <h1>🐛 Bug Report Generator</h1>
        <p>Convert failure analysis into professional, structured bug reports ready for Jira or your tracking tool</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Auto-load from other pages ───────────────────────────────────────────
    auto_source = None
    if "bug_from_log" in st.session_state:
        st.info("📥 Auto-loaded from Log Analyser. Review and generate the report.")
        auto_source = "log"
    elif "bug_from_screenshot" in st.session_state:
        st.info("📥 Auto-loaded from Screenshot Analyser. Review and generate the report.")
        auto_source = "screenshot"

    # ── Mode selection ────────────────────────────────────────────────────────
    tab1, tab2 = st.tabs(["📝 Manual / Paste Input", "🤖 From Analysis (Auto)"])

    # ── Tab 1: Manual ─────────────────────────────────────────────────────────
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            test_case = st.text_input("Related Test Case ID", placeholder="TC-001, TC-042")
            environment = st.text_input("Environment", value="QA Environment")
        with col2:
            severity_hint = st.selectbox("Suspected Severity", ["Auto-detect", "Critical", "High", "Medium", "Low"])
            component = st.text_input("Component / Module", placeholder="Login module, Payment API...")

        failure_desc = st.text_area(
            "Failure Description / Observed Behaviour",
            height=200,
            placeholder="Describe what went wrong, paste error messages, stack traces, or failure analysis here...",
        )
        notes = st.text_area("Additional Notes", height=100, placeholder="Steps you took, related tickets, screenshots taken...")

        generate_btn = st.button("🐛 Generate Bug Report", type="primary", key="manual_gen")

        if generate_btn:
            if not failure_desc.strip():
                st.warning("Please provide a failure description.")
            else:
                if not st.session_state.get("api_key") and st.session_state.get("llm_provider") != "Ollama (Local)":
                    st.error("Please configure your API key in the sidebar.")
                else:
                    with st.spinner("🤖 Generating bug report..."):
                        try:
                            report = generate_bug_report(
                                failure_desc,
                                test_case=test_case,
                                environment=environment,
                                notes=notes,
                            )
                            st.session_state["bug_report"] = report
                        except Exception as e:
                            st.error(f"Generation error: {e}")

    # ── Tab 2: From analysis ──────────────────────────────────────────────────
    with tab2:
        if auto_source == "log":
            analysis_data = st.session_state.get("bug_from_log", {})
        elif auto_source == "screenshot":
            analysis_data = st.session_state.get("bug_from_screenshot", {})
        else:
            analysis_data = {}

        if analysis_data:
            with st.expander("📋 Source Analysis Data"):
                st.json(analysis_data)

            context = st.text_input("Additional context (optional)", key="auto_ctx")
            auto_gen_btn = st.button("🐛 Generate Bug Report from Analysis", type="primary", key="auto_gen")

            if auto_gen_btn:
                if not st.session_state.get("api_key") and st.session_state.get("llm_provider") != "Ollama (Local)":
                    st.error("Please configure your API key in the sidebar.")
                else:
                    with st.spinner("🤖 Generating bug report from analysis..."):
                        try:
                            report = generate_from_log_analysis(analysis_data, context)
                            st.session_state["bug_report"] = report
                            # Clear auto-load flags
                            st.session_state.pop("bug_from_log", None)
                            st.session_state.pop("bug_from_screenshot", None)
                        except Exception as e:
                            st.error(f"Generation error: {e}")
        else:
            st.info("No analysis data available. Run Log Analyser or Screenshot Analyser first, then click 'Generate Bug Report'.")

    # ── Display report ────────────────────────────────────────────────────────
    if "bug_report" in st.session_state:
        report = st.session_state["bug_report"]
        st.markdown("---")
        st.subheader("📋 Generated Bug Report")

        # Header
        sev = report.get("severity", "Medium")
        prio = report.get("priority", "P2")
        st.markdown(
            f"## 🐛 {report.get('title', 'Bug Report')}\n"
            f"**ID:** `{report.get('bug_id', 'BUG-001')}` &nbsp;&nbsp;"
            f"{_sev_badge(sev)} &nbsp;&nbsp; **Priority:** {prio} &nbsp;&nbsp; "
            f"**Type:** {report.get('bug_type', '')} &nbsp;&nbsp; "
            f"**Component:** {report.get('component', '')}",
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**📝 Summary**")
            st.info(report.get("summary", ""))

            st.markdown("**🔬 Root Cause**")
            st.warning(report.get("root_cause", ""))

            st.markdown("**💥 Impact**")
            st.markdown(report.get("impact", ""))

            env = report.get("environment", {})
            if isinstance(env, dict):
                st.markdown("**🖥️ Environment**")
                for k, v in env.items():
                    if v:
                        st.markdown(f"- **{k.replace('_', ' ').title()}:** {v}")

        with col2:
            st.markdown("**🪜 Steps to Reproduce**")
            steps = report.get("steps_to_reproduce", [])
            if isinstance(steps, list):
                for i, step in enumerate(steps, 1):
                    st.markdown(f"{i}. {step}")

            st.markdown("**❌ Actual Result**")
            st.markdown(report.get("actual_result", ""))

            st.markdown("**✅ Expected Result**")
            st.markdown(report.get("expected_result", ""))

        recs = report.get("recommendations", [])
        if recs:
            st.markdown("**💡 Recommendations**")
            for r in recs:
                st.markdown(f"- {r}")

        if report.get("logs_excerpt"):
            with st.expander("📜 Log Evidence"):
                st.code(report["logs_excerpt"], language="text")

        # Labels
        labels = report.get("suggested_labels", [])
        if labels:
            st.markdown("**🏷️ Suggested Labels:** " + " ".join(f"`{l}`" for l in labels))

        st.markdown(f"**⏱️ Estimated Fix Effort:** {report.get('estimated_fix_effort', 'Unknown')}")

        # ── Export ───────────────────────────────────────────────────────────
        st.markdown("---")
        st.subheader("📤 Export")
        col1, col2, col3 = st.columns(3)

        with col1:
            try:
                word_bytes = bug_report_to_word(report)
                st.download_button(
                    "📄 Download Word (.docx)",
                    data=word_bytes,
                    file_name=f"{report.get('bug_id', 'bug_report')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Word export error: {e}")

        with col2:
            st.download_button(
                "📋 Download JSON",
                data=to_json_bytes(report),
                file_name=f"{report.get('bug_id', 'bug_report')}.json",
                mime="application/json",
                use_container_width=True,
            )

        with col3:
            if st.button("📡 Format for Jira", use_container_width=True):
                with st.spinner("Formatting for Jira..."):
                    try:
                        jira_payload = format_for_jira(report)
                        st.session_state["jira_payload"] = jira_payload
                    except Exception as e:
                        st.error(f"Jira format error: {e}")

        if "jira_payload" in st.session_state:
            with st.expander("📡 Jira Payload (REST API)"):
                st.json(st.session_state["jira_payload"])
                st.caption("Use this JSON body with POST /rest/api/3/issue")
