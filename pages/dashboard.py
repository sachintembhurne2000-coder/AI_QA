"""Dashboard page with session history and analytics"""
import streamlit as st
import json
from datetime import datetime


def render():
    st.markdown("""
    <div class="main-header">
        <h1>📊 Dashboard</h1>
        <p>Session history, coverage analytics, and AI generation statistics</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Session summary metrics ───────────────────────────────────────────────
    test_cases = st.session_state.get("test_cases", [])
    bug_report = st.session_state.get("bug_report", {})
    log_analysis = st.session_state.get("log_analysis", {})
    generated_code = st.session_state.get("generated_code", {})
    api_summary = st.session_state.get("api_summary", {})

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🧪 Test Cases", len(test_cases))
    col2.metric("📄 Code Files", len(generated_code))
    col3.metric("🔌 API Endpoints", len(api_summary.get("endpoints", [])))
    col4.metric("🐛 Bug Reports", 1 if bug_report else 0)
    col5.metric("📋 Log Analyses", 1 if log_analysis else 0)

    st.markdown("---")

    if not test_cases and not log_analysis and not bug_report:
        st.info("📊 Dashboard will show analytics once you've used the tools. Start with the **Test Case Generator** or **Log Analyser**.")

        # Show demo charts placeholder
        st.subheader("📈 Example Dashboard (Demo Data)")
        _show_demo_charts()
        return

    # ── Test case analytics ───────────────────────────────────────────────────
    if test_cases:
        st.subheader("🧪 Test Case Analytics")
        _show_test_case_charts(test_cases)

    # ── Log analysis summary ──────────────────────────────────────────────────
    if log_analysis:
        st.markdown("---")
        st.subheader("🔍 Latest Log Analysis")
        _show_log_summary(log_analysis)

    # ── Bug report summary ────────────────────────────────────────────────────
    if bug_report:
        st.markdown("---")
        st.subheader("🐛 Latest Bug Report")
        col1, col2, col3 = st.columns(3)
        col1.metric("Severity", bug_report.get("severity", "Unknown"))
        col2.metric("Priority", bug_report.get("priority", "Unknown"))
        col3.metric("Est. Fix Effort", bug_report.get("estimated_fix_effort", "Unknown"))
        st.info(f"**{bug_report.get('title', '')}:** {bug_report.get('summary', '')}")

    # ── Session state inspector ────────────────────────────────────────────────
    with st.expander("🔧 Session State Inspector (Debug)"):
        keys = [k for k in st.session_state.keys() if not k.startswith("_")]
        for k in keys:
            v = st.session_state[k]
            if isinstance(v, (dict, list)):
                st.markdown(f"**{k}:** `{type(v).__name__}` with {len(v)} items")
            else:
                st.markdown(f"**{k}:** `{str(v)[:100]}`")


def _show_test_case_charts(test_cases):
    try:
        import plotly.express as px
        import pandas as pd

        col1, col2 = st.columns(2)

        with col1:
            # Priority breakdown
            priorities = [tc.get("priority", "Medium") for tc in test_cases]
            priority_counts = {}
            for p in priorities:
                priority_counts[p] = priority_counts.get(p, 0) + 1

            fig = px.pie(
                values=list(priority_counts.values()),
                names=list(priority_counts.keys()),
                title="Test Cases by Priority",
                color_discrete_map={
                    "Critical": "#FF0000",
                    "High": "#FF6B35",
                    "Medium": "#F6AD55",
                    "Low": "#68D391",
                },
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Type breakdown
            types = [tc.get("type", "Functional") for tc in test_cases]
            type_counts = {}
            for t in types:
                type_counts[t] = type_counts.get(t, 0) + 1

            fig2 = px.bar(
                x=list(type_counts.keys()),
                y=list(type_counts.values()),
                title="Test Cases by Type",
                labels={"x": "Type", "y": "Count"},
                color=list(type_counts.values()),
                color_continuous_scale="Blues",
            )
            fig2.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

        # Steps distribution
        step_counts = [len(tc.get("steps", [])) for tc in test_cases]
        import plotly.graph_objects as go
        fig3 = go.Figure(data=[go.Histogram(x=step_counts, nbinsx=8,
                                             marker_color="#2B6CB0")])
        fig3.update_layout(title="Distribution of Steps per Test Case",
                           xaxis_title="Number of Steps",
                           yaxis_title="Count", height=250)
        st.plotly_chart(fig3, use_container_width=True)

    except ImportError:
        st.warning("Install plotly for charts: pip install plotly")
        # Fallback text summary
        priorities = [tc.get("priority", "Medium") for tc in test_cases]
        for p in ["Critical", "High", "Medium", "Low"]:
            st.markdown(f"- **{p}:** {priorities.count(p)}")


def _show_log_summary(analysis):
    col1, col2, col3 = st.columns(3)
    col1.metric("Status", analysis.get("overall_status", "Unknown"))
    col2.metric("Errors Found", len(analysis.get("errors_found", [])))
    col3.metric("Root Causes", len(analysis.get("root_causes", [])))

    try:
        import plotly.express as px

        root_causes = analysis.get("root_causes", [])
        if root_causes:
            categories = [rc.get("category", "Unknown") for rc in root_causes]
            cat_counts = {}
            for c in categories:
                cat_counts[c] = cat_counts.get(c, 0) + 1

            fig = px.bar(
                x=list(cat_counts.keys()),
                y=list(cat_counts.values()),
                title="Root Cause Categories",
                color=list(cat_counts.values()),
                color_continuous_scale="Reds",
            )
            fig.update_layout(height=250, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        pass


def _show_demo_charts():
    """Show demo charts with fake data."""
    try:
        import plotly.express as px

        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(
                values=[5, 12, 18, 8],
                names=["Critical", "High", "Medium", "Low"],
                title="Sample: Test Cases by Priority",
                color_discrete_map={"Critical": "#FF0000", "High": "#FF6B35",
                                    "Medium": "#F6AD55", "Low": "#68D391"},
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig2 = px.bar(
                x=["Functional", "Negative", "Boundary", "Security", "UI"],
                y=[15, 10, 8, 4, 6],
                title="Sample: Test Cases by Type",
                color=[15, 10, 8, 4, 6],
                color_continuous_scale="Blues",
            )
            fig2.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

    except ImportError:
        st.info("Install plotly for interactive charts: pip install plotly")
