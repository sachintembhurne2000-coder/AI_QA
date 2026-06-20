"""Home / landing page"""
import streamlit as st


def render():
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI QA Copilot</h1>
        <p>Your end-to-end AI-powered quality assurance assistant for embedded systems, web apps, and APIs</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick stats row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🧪 Features", "13", "Core + Enhanced")
    col2.metric("🤖 AI Agents", "5", "Specialised")
    col3.metric("📤 Export Formats", "5", "Excel·Word·JSON·ZIP")
    col4.metric("🔌 Protocols", "4", "MQTT·KNX·BACnet·Modbus")

    st.markdown("---")

    # Feature cards
    st.subheader("🚀 What can AI QA Copilot do?")

    features = [
        ("📋", "Test Case Generator", "Upload requirements (PDF/DOCX/TXT) → AI generates structured test cases with steps, priority, and expected results.", "Core"),
        ("🤖", "Automation Code Gen", "Convert test cases into runnable Playwright, Selenium POM, or Pytest automation code instantly.", "Core"),
        ("🔌", "API Test Generator", "Parse OpenAPI/Swagger specs and generate complete Pytest + HTTPX API test suites.", "Core"),
        ("🔍", "Log Analyser", "Upload test, server, or embedded device logs → AI identifies root causes with confidence scores.", "Core"),
        ("🖼️", "Screenshot Analyser", "Upload UI screenshots → AI detects defects, layout issues, and missing elements via GPT Vision.", "Core"),
        ("🐛", "Bug Report Generator", "Convert failure analysis into professional bug reports. Export to Word or Jira format.", "Core"),
        ("🧠", "RAG Knowledge Base", "Store requirements, SOPs, and standards — AI uses them for context-aware generation.", "Enhanced"),
        ("📊", "Dashboard", "View session history, test coverage stats, and failure trends with interactive charts.", "Enhanced"),
    ]

    col1, col2 = st.columns(2)
    for i, (icon, title, desc, tier) in enumerate(features):
        badge_class = "badge-core" if tier == "Core" else "badge-enhanced"
        html = f"""
        <div class="feature-card">
            <h4>{icon} {title} <span class="{badge_class}">{tier}</span></h4>
            <p>{desc}</p>
        </div>
        """
        if i % 2 == 0:
            col1.markdown(html, unsafe_allow_html=True)
        else:
            col2.markdown(html, unsafe_allow_html=True)

    st.markdown("---")

    # Getting started
    st.subheader("⚡ Getting Started")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **Step 1 — Configure LLM**
        1. Open the **sidebar** ←
        2. Select your LLM provider
        3. Enter your API key
        4. Choose a model
        """)

    with col2:
        st.markdown("""
        **Step 2 — Pick a Tool**
        1. Navigate using the sidebar menu
        2. Upload your document or logs
        3. Click **Generate / Analyse**
        4. Review AI output
        """)

    with col3:
        st.markdown("""
        **Step 3 — Export Results**
        1. Download as Excel, Word, or JSON
        2. Copy automation code to your IDE
        3. Create Jira tickets from bug reports
        4. Build your regression suite
        """)

    st.markdown("---")
    st.info("💡 **Tip:** Add your requirements, test standards, and coding guidelines to the **RAG Knowledge Base** first — this improves the quality of all AI-generated outputs across all tools.")

    # API Key check
    if not st.session_state.get("api_key"):
        st.warning("⚠️ No API key configured. Please enter your API key in the sidebar to use AI features.")
    else:
        provider = st.session_state.get("llm_provider", "")
        model = st.session_state.get("model", "")
        st.success(f"✅ LLM configured: **{provider}** · Model: **{model}**")
