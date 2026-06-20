"""Automation Code Generator page"""
import streamlit as st
import json
from agents.automation_agent import (
    generate_playwright, generate_selenium, generate_pytest,
    generate_api_tests, parse_code_sections,
)
from services.export import create_zip


def render():
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Automation Code Generator</h1>
        <p>Convert test cases into runnable Playwright, Selenium POM, or Pytest automation code</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Input source ─────────────────────────────────────────────────────────
    st.subheader("📥 Input: Test Cases")

    source = st.radio(
        "Source",
        ["Use test cases from Test Case Generator", "Paste JSON manually"],
        horizontal=True,
    )

    test_cases = []
    if source == "Use test cases from Test Case Generator":
        if "test_cases" in st.session_state:
            test_cases = st.session_state["test_cases"]
            st.success(f"✅ Loaded {len(test_cases)} test cases from session")
        elif "tc_for_automation" in st.session_state:
            test_cases = st.session_state["tc_for_automation"]
            st.success(f"✅ Loaded {len(test_cases)} test cases")
        else:
            st.warning("No test cases in session. Generate them first or paste JSON below.")
    else:
        json_input = st.text_area(
            "Paste test cases JSON array",
            height=200,
            placeholder='[{"id":"TC-001","title":"Login with valid credentials","steps":["Navigate to login","Enter username","Enter password","Click login"],"expected_result":"User is redirected to dashboard"}]',
        )
        if json_input.strip():
            try:
                test_cases = json.loads(json_input)
                st.success(f"✅ Parsed {len(test_cases)} test cases")
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON: {e}")

    if test_cases:
        # Select subset
        tc_titles = [f"{tc.get('id', i)} — {tc.get('title', '')}" for i, tc in enumerate(test_cases)]
        selected = st.multiselect(
            "Select test cases to include",
            tc_titles,
            default=tc_titles[:10],
        )
        selected_indices = [tc_titles.index(s) for s in selected]
        test_cases = [test_cases[i] for i in selected_indices]

    # ── Framework selection ──────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("🔧 Framework & Options")

    col1, col2 = st.columns(2)
    with col1:
        framework = st.selectbox(
            "Automation Framework",
            [
                "Playwright (Python + pytest-playwright)",
                "Selenium WebDriver (POM pattern)",
                "Pytest (API / Unit tests)",
                "Pytest + HTTPX (API tests)",
            ],
        )
    with col2:
        base_url = st.text_input(
            "Application Base URL",
            value="https://your-app.com",
            help="Used in generated page objects and API clients",
        )

    generate_btn = st.button("⚡ Generate Automation Code", type="primary")

    # ── Generate ─────────────────────────────────────────────────────────────
    if generate_btn:
        if not test_cases:
            st.warning("No test cases selected.")
            return
        if not st.session_state.get("api_key") and st.session_state.get("llm_provider") != "Ollama (Local)":
            st.error("Please configure your API key in the sidebar.")
            return

        with st.spinner(f"🤖 Generating {framework} code... (20-40 seconds)"):
            try:
                if "Playwright" in framework:
                    raw_code = generate_playwright(test_cases)
                elif "Selenium" in framework:
                    raw_code = generate_selenium(test_cases)
                elif "HTTPX" in framework:
                    raw_code = generate_api_tests(test_cases, base_url)
                else:
                    raw_code = generate_pytest(test_cases)

                sections = parse_code_sections(raw_code)
                st.session_state["generated_code"] = sections
                st.session_state["raw_code"] = raw_code
            except Exception as e:
                st.error(f"Code generation error: {e}")
                return

    # ── Display generated code ────────────────────────────────────────────────
    if "generated_code" in st.session_state:
        sections = st.session_state["generated_code"]
        st.markdown("---")
        st.subheader(f"✅ Generated {len(sections)} File(s)")

        # Tabs per file
        if len(sections) > 1:
            tabs = st.tabs(list(sections.keys()))
            for tab, (filename, code) in zip(tabs, sections.items()):
                with tab:
                    st.code(code, language="python")
        else:
            for filename, code in sections.items():
                st.subheader(f"📄 {filename}")
                st.code(code, language="python")

        # Export
        st.markdown("---")
        st.subheader("📤 Export")
        col1, col2 = st.columns(2)

        with col1:
            # ZIP with all files
            zip_files = {name: code.encode() for name, code in sections.items()}
            zip_bytes = create_zip(zip_files)
            st.download_button(
                "📦 Download ZIP (all files)",
                data=zip_bytes,
                file_name="automation_code.zip",
                mime="application/zip",
                use_container_width=True,
            )
        with col2:
            # Raw as single file
            raw = st.session_state.get("raw_code", "")
            st.download_button(
                "📄 Download as single .py",
                data=raw.encode(),
                file_name="automation_tests.py",
                mime="text/plain",
                use_container_width=True,
            )

        # Requirements
        st.markdown("---")
        st.subheader("📦 Required Packages")
        framework_sel = framework if "generated_code" in st.session_state else ""
        if "Playwright" in framework_sel:
            st.code("pip install pytest pytest-playwright\npython -m playwright install chromium", language="bash")
        elif "Selenium" in framework_sel:
            st.code("pip install selenium pytest webdriver-manager", language="bash")
        elif "HTTPX" in framework_sel:
            st.code("pip install pytest httpx", language="bash")
        else:
            st.code("pip install pytest", language="bash")
