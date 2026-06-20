"""API Test Generator page"""
import streamlit as st
import json
import pandas as pd
from agents.api_agent import parse_spec, generate_api_test_suite, suggest_test_cases, load_spec
from services.parser import parse_document
from services.export import test_cases_to_excel, create_zip, to_json_bytes


def render():
    st.markdown("""
    <div class="main-header">
        <h1>🔌 API Test Generator</h1>
        <p>Upload OpenAPI/Swagger specs → AI generates complete Pytest + HTTPX test suites</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Upload ───────────────────────────────────────────────────────────────
    col1, col2 = st.columns([1, 1])
    with col1:
        uploaded = st.file_uploader(
            "Upload OpenAPI / Swagger spec",
            type=["yaml", "yml", "json"],
            help="OpenAPI 3.x or Swagger 2.x YAML or JSON",
        )
    with col2:
        st.markdown("**— or paste spec below —**")
        pasted = st.text_area(
            "OpenAPI spec (YAML or JSON)",
            height=150,
            placeholder="openapi: 3.0.0\ninfo:\n  title: My API...",
            label_visibility="collapsed",
        )

    spec_text = ""
    if uploaded:
        spec_text = uploaded.read().decode("utf-8", errors="replace")
        st.success(f"✅ Loaded: **{uploaded.name}** ({len(spec_text):,} chars)")
    elif pasted.strip():
        spec_text = pasted.strip()

    if spec_text:
        with st.expander("👀 Preview spec (first 1000 chars)"):
            st.code(spec_text[:1000], language="yaml")

    col1, col2 = st.columns(2)
    with col1:
        analyse_btn = st.button("🔍 Analyse API Spec", use_container_width=True)
    with col2:
        generate_btn = st.button("⚡ Generate Test Suite", type="primary", use_container_width=True)

    # ── Analyse spec ─────────────────────────────────────────────────────────
    if analyse_btn and spec_text:
        with st.spinner("🧠 Analysing API spec..."):
            try:
                summary = parse_spec(spec_text)
                st.session_state["api_summary"] = summary
                test_cases = suggest_test_cases(summary)
                st.session_state["api_test_cases"] = test_cases
            except Exception as e:
                st.error(f"Analysis error: {e}")
                return

    if "api_summary" in st.session_state:
        summary = st.session_state["api_summary"]
        st.markdown("---")
        st.subheader("📑 API Analysis")

        col1, col2, col3 = st.columns(3)
        col1.metric("API Title", summary.get("title", "Unknown")[:30])
        col2.metric("Endpoints", len(summary.get("endpoints", [])))
        col3.metric("Auth Type", summary.get("auth_type", "unknown"))

        st.markdown(f"**Base URL:** `{summary.get('base_url', 'Not specified')}`")

        with st.expander("📋 Endpoints"):
            endpoints = summary.get("endpoints", [])
            if endpoints:
                df = pd.DataFrame([{
                    "Method": ep.get("method", ""),
                    "Path": ep.get("path", ""),
                    "Description": ep.get("description", ""),
                } for ep in endpoints])
                st.dataframe(df, use_container_width=True, hide_index=True)

        if "api_test_cases" in st.session_state:
            tcs = st.session_state["api_test_cases"]
            st.subheader(f"🧪 Suggested Test Cases ({len(tcs)})")
            df = pd.DataFrame([{
                "ID": tc.get("id", ""),
                "Endpoint": tc.get("endpoint", ""),
                "Title": tc.get("title", ""),
                "Type": tc.get("type", ""),
                "Priority": tc.get("priority", ""),
                "Expected Status": tc.get("expected_status", ""),
            } for tc in tcs])
            st.dataframe(df, use_container_width=True, hide_index=True)

            col1, col2 = st.columns(2)
            with col1:
                excel = test_cases_to_excel(tcs)
                st.download_button("📊 Export Test Cases (Excel)", excel,
                                   "api_test_cases.xlsx", use_container_width=True)
            with col2:
                js = to_json_bytes(tcs)
                st.download_button("📋 Export Test Cases (JSON)", js,
                                   "api_test_cases.json", use_container_width=True)

    # ── Generate test suite ───────────────────────────────────────────────────
    if generate_btn:
        if not spec_text:
            st.warning("Please upload or paste an OpenAPI spec first.")
            return
        if not st.session_state.get("api_key") and st.session_state.get("llm_provider") != "Ollama (Local)":
            st.error("Please configure your API key in the sidebar.")
            return

        summary = st.session_state.get("api_summary")
        if not summary:
            with st.spinner("Analysing spec..."):
                try:
                    summary = parse_spec(spec_text)
                    st.session_state["api_summary"] = summary
                except Exception as e:
                    st.error(f"Analysis error: {e}")
                    return

        with st.spinner("⚡ Generating Pytest + HTTPX test suite... (30-60 seconds)"):
            try:
                code = generate_api_test_suite(spec_text, summary)
                st.session_state["api_code"] = code
            except Exception as e:
                st.error(f"Generation error: {e}")
                return

    if "api_code" in st.session_state:
        code = st.session_state["api_code"]
        st.markdown("---")
        st.subheader("✅ Generated API Test Suite")
        st.code(code, language="python")

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📦 Download ZIP",
                data=create_zip({"api_tests.py": code.encode()}),
                file_name="api_test_suite.zip",
                mime="application/zip",
                use_container_width=True,
            )
        with col2:
            st.download_button(
                "📄 Download .py",
                data=code.encode(),
                file_name="api_tests.py",
                mime="text/plain",
                use_container_width=True,
            )

        st.markdown("**Required packages:**")
        st.code("pip install pytest httpx pytest-asyncio", language="bash")
