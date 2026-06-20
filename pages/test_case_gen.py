"""Test Case Generator page"""
import streamlit as st
import json
import pandas as pd
from services.parser import parse_document
from agents.requirement_agent import extract_requirements, generate_test_cases
from services.export import test_cases_to_excel, to_json_bytes, create_zip
from services.rag import add_document


def render():
    st.markdown("""
    <div class="main-header">
        <h1>📋 Test Case Generator</h1>
        <p>Upload requirements documents → AI generates comprehensive, structured test cases</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar options ──────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("---")
        st.markdown("**📋 Generator Settings**")
        max_cases = st.slider("Max test cases", 5, 50, 20)
        use_rag = st.checkbox("Use knowledge base context", value=True)
        include_negative = st.checkbox("Include negative tests", value=True)
        include_boundary = st.checkbox("Include boundary tests", value=True)
        add_to_kb = st.checkbox("Add doc to knowledge base", value=False)

    # ── Upload ───────────────────────────────────────────────────────────────
    uploaded = st.file_uploader(
        "Upload requirements document",
        type=["pdf", "docx", "txt", "md"],
        help="Supports PDF, Word DOCX, TXT, and Markdown",
    )

    st.markdown("**— or paste requirements directly —**")
    pasted_text = st.text_area(
        "Requirements text",
        height=200,
        placeholder="Paste your requirements, user stories, or acceptance criteria here...",
        label_visibility="collapsed",
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        generate_btn = st.button("🚀 Generate Test Cases", type="primary", use_container_width=True)
    with col2:
        analyse_btn = st.button("📑 Analyse Requirements Only", use_container_width=True)

    # ── Process ──────────────────────────────────────────────────────────────
    doc_text = ""
    if uploaded:
        with st.spinner("Parsing document..."):
            doc_text = parse_document(uploaded, uploaded.name)
        st.success(f"✅ Parsed: **{uploaded.name}** ({len(doc_text):,} chars)")

        if add_to_kb:
            with st.spinner("Adding to knowledge base..."):
                n = add_document(doc_text, uploaded.name, doc_type="requirements")
            st.info(f"📚 Added {n} chunks to knowledge base.")

    elif pasted_text.strip():
        doc_text = pasted_text.strip()

    # ── Analyse requirements ──────────────────────────────────────────────────
    if analyse_btn and doc_text:
        with st.spinner("🧠 Analysing requirements..."):
            try:
                analysis = extract_requirements(doc_text)
                st.session_state["req_analysis"] = analysis
            except Exception as e:
                st.error(f"Analysis error: {e}")
                return

    if "req_analysis" in st.session_state:
        analysis = st.session_state["req_analysis"]
        st.subheader("📑 Requirements Analysis")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Summary**")
            st.info(analysis.get("summary", ""))

            st.markdown("**Actors / Users**")
            for a in analysis.get("actors", []):
                st.markdown(f"- {a}")

        with col2:
            st.markdown("**Functional Requirements**")
            for r in analysis.get("functional_requirements", []):
                st.markdown(f"- {r}")

            st.markdown("**Edge Cases to Consider**")
            for e in analysis.get("edge_cases", []):
                st.markdown(f"⚠️ {e}")

        st.markdown("**Acceptance Criteria**")
        for c in analysis.get("acceptance_criteria", []):
            st.markdown(f"✅ {c}")

    # ── Generate test cases ───────────────────────────────────────────────────
    if generate_btn:
        if not doc_text:
            st.warning("Please upload a document or paste requirements text first.")
            return
        if not st.session_state.get("api_key") and st.session_state.get("llm_provider") != "Ollama (Local)":
            st.error("Please configure your API key in the sidebar.")
            return

        with st.spinner("🤖 Generating test cases... (this may take 15-30 seconds)"):
            try:
                test_cases = generate_test_cases(
                    doc_text,
                    max_cases=max_cases,
                    use_rag=use_rag,
                )
                st.session_state["test_cases"] = test_cases
            except Exception as e:
                st.error(f"Generation error: {e}")
                return

    # ── Display results ───────────────────────────────────────────────────────
    if "test_cases" in st.session_state:
        tcs = st.session_state["test_cases"]
        st.markdown("---")
        st.subheader(f"✅ Generated {len(tcs)} Test Cases")

        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        priorities = [tc.get("priority", "Medium") for tc in tcs]
        types = [tc.get("type", "Functional") for tc in tcs]
        col1.metric("Critical", priorities.count("Critical"))
        col2.metric("High", priorities.count("High"))
        col3.metric("Medium", priorities.count("Medium"))
        col4.metric("Low", priorities.count("Low"))

        # Filter controls
        col1, col2 = st.columns(2)
        with col1:
            filter_priority = st.multiselect(
                "Filter by Priority",
                ["Critical", "High", "Medium", "Low"],
                default=["Critical", "High", "Medium", "Low"],
            )
        with col2:
            filter_type = st.multiselect(
                "Filter by Type",
                list(set(types)),
                default=list(set(types)),
            )

        filtered = [
            tc for tc in tcs
            if tc.get("priority", "Medium") in filter_priority
            and tc.get("type", "Functional") in filter_type
        ]

        # Table view
        df = pd.DataFrame([{
            "ID": tc.get("id", ""),
            "Title": tc.get("title", ""),
            "Type": tc.get("type", ""),
            "Priority": tc.get("priority", ""),
            "Steps": len(tc.get("steps", [])),
        } for tc in filtered])

        st.dataframe(df, use_container_width=True, hide_index=True)

        # Detail expander per test case
        st.subheader("📄 Test Case Details")
        for tc in filtered[:15]:  # Show max 15 details
            priority_icon = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(tc.get("priority", ""), "⚪")
            with st.expander(f"{priority_icon} {tc.get('id')} — {tc.get('title', '')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Type:** {tc.get('type', '')}")
                    st.markdown(f"**Priority:** {tc.get('priority', '')}")
                    st.markdown(f"**Preconditions:** {tc.get('preconditions', 'None')}")
                with col2:
                    st.markdown("**Steps:**")
                    for i, step in enumerate(tc.get("steps", []), 1):
                        st.markdown(f"{i}. {step}")
                st.markdown(f"**Expected Result:** {tc.get('expected_result', '')}")

        # Export
        st.markdown("---")
        st.subheader("📤 Export")
        col1, col2, col3 = st.columns(3)

        with col1:
            excel_bytes = test_cases_to_excel(tcs)
            st.download_button(
                "📊 Download Excel",
                data=excel_bytes,
                file_name="test_cases.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        with col2:
            json_bytes = to_json_bytes(tcs)
            st.download_button(
                "📋 Download JSON",
                data=json_bytes,
                file_name="test_cases.json",
                mime="application/json",
                use_container_width=True,
            )
        with col3:
            if st.button("➡️ Send to Automation Generator", use_container_width=True):
                st.session_state["tc_for_automation"] = tcs
                st.success("Test cases sent! Navigate to 🤖 Automation Code Gen")
