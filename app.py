"""
AI QA Copilot - Main Application Entry Point
"""
import streamlit as st
import os
from pathlib import Path

# Page config - must be first Streamlit call
st.set_page_config(
    page_title="AI QA Copilot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Ensure required directories exist
for d in ["uploads", "reports", "automation", "knowledge"]:
    Path(d).mkdir(exist_ok=True)

# Custom CSS
st.markdown("""
<style>
    /* Main theme */
    .main-header {
        background: linear-gradient(135deg, #1E3A5F 0%, #2B6CB0 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .main-header h1 { color: white; margin: 0; font-size: 2rem; }
    .main-header p { color: #BEE3F8; margin: 0.3rem 0 0 0; font-size: 1rem; }

    /* Feature cards */
    .feature-card {
        background: #F7FAFC;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #2B6CB0;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    .feature-card h4 { color: #1E3A5F; margin: 0 0 0.3rem 0; }
    .feature-card p { color: #4A5568; margin: 0; font-size: 0.9rem; }

    /* Status badges */
    .badge-core { background:#C6F6D5; color:#276749; padding:2px 8px; border-radius:12px; font-size:0.75rem; }
    .badge-enhanced { background:#BEE3F8; color:#1A365D; padding:2px 8px; border-radius:12px; font-size:0.75rem; }
    .badge-optional { background:#FED7AA; color:#744210; padding:2px 8px; border-radius:12px; font-size:0.75rem; }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 0.8rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }

    /* Sidebar */
    .css-1d391kg { background: #F0F4F8; }

    /* Success/Info boxes */
    .stSuccess { border-radius: 8px; }
    .stInfo { border-radius: 8px; }

    /* Code blocks */
    .stCodeBlock { border-radius: 8px; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0 0;
        background: #EBF4FF;
        color: #2B6CB0;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar Navigation ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 0.5rem 0 1.2rem 0;">
        <div style="font-size:2.5rem;">🤖</div>
        <div style="font-weight:700; font-size:1.1rem; color:#1E3A5F;">AI QA Copilot</div>
        <div style="font-size:0.75rem; color:#718096;">v1.0 · Hackathon Edition</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    page = st.radio(
        "Navigate",
        [
            "🏠 Home",
            "📋 Test Case Generator",
            "🤖 Automation Code Gen",
            "🔌 API Test Generator",
            "🔍 Log Analyser",
            "🖼️ Screenshot Analyser",
            "🐛 Bug Report Generator",
            "🧠 RAG Knowledge Base",
            "📊 Dashboard",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("**⚙️ LLM Settings**")

    llm_provider = st.selectbox(
        "Provider",
        ["Claude (Anthropic)", "OpenAI GPT-4", "Ollama (Local)"],
        key="llm_provider",
    )

    if llm_provider == "Claude (Anthropic)":
        api_key = st.text_input("Anthropic API Key", type="password", key="anthropic_key",
                                 placeholder="sk-ant-...")
        model = st.selectbox("Model", ["claude-sonnet-4-6"], key="claude_model")
    elif llm_provider == "OpenAI GPT-4":
        api_key = st.text_input("OpenAI API Key", type="password", key="openai_key",
                                 placeholder="sk-...")
        model = st.selectbox("Model", ["gpt-4o", "gpt-4-turbo", "gpt-4"], key="oai_model")
    else:
        api_key = ""
        ollama_models = [
            "Select a model...",
            "deepseek-r1:8b",
            "openhermes:v2.5",
            "phi3:3.8b",
            "deepseek-coder:6.7b",
            "qwen2.5-coder:7b",
            "llama2:latest",
            "llama3.2",
        ]
        # Determine a safe default index (use placeholder by default)
        default_idx = 0
        if "ollama_model" in st.session_state and st.session_state.get("ollama_model") in ollama_models:
            default_idx = ollama_models.index(st.session_state.get("ollama_model"))

        model = st.selectbox("Ollama Model", ollama_models, index=default_idx, key="ollama_model")
        st.caption("Make sure Ollama is running on localhost:11434")

    # Store in session (avoid overwriting widget-managed keys)
    if "llm_provider" not in st.session_state:
        st.session_state["llm_provider"] = llm_provider
    st.session_state["api_key"] = api_key
    # Only store the model if user explicitly selected one (not the placeholder)
    if model and model != "Select a model...":
        st.session_state["model"] = model
    else:
        # Remove any previous model selection to force explicit runtime choice
        if "model" in st.session_state:
            del st.session_state["model"]

    st.markdown("---")
    st.caption("Built for hackathon demo · Uses Anthropic/OpenAI APIs")

# ── Page Router ─────────────────────────────────────────────────────────────
if page == "🏠 Home":
    from pages.home import render
    render()
elif page == "📋 Test Case Generator":
    from pages.test_case_gen import render
    render()
elif page == "🤖 Automation Code Gen":
    from pages.automation_gen import render
    render()
elif page == "🔌 API Test Generator":
    from pages.api_test_gen import render
    render()
elif page == "🔍 Log Analyser":
    from pages.log_analyser import render
    render()
elif page == "🖼️ Screenshot Analyser":
    from pages.screenshot_analyser import render
    render()
elif page == "🐛 Bug Report Generator":
    from pages.bug_report import render
    render()
elif page == "🧠 RAG Knowledge Base":
    from pages.rag_kb import render
    render()
elif page == "📊 Dashboard":
    from pages.dashboard import render
    render()
