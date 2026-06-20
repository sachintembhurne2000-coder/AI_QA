# 🤖 AI QA Copilot

> End-to-end AI-powered quality assurance assistant for embedded systems, web applications, and APIs.

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ✨ Features

| Feature | Description | Tier |
|---|---|---|
| 📋 Test Case Generator | Upload requirements → structured test cases | Core |
| 🤖 Automation Code Gen | Test cases → Playwright / Selenium / Pytest code | Core |
| 🔌 API Test Generator | OpenAPI spec → Pytest + HTTPX test suite | Core |
| 🔍 Log Analyser | Logs → root cause analysis (incl. MQTT/KNX/BACnet) | Core |
| 🖼️ Screenshot Analyser | UI screenshot → defect detection via AI Vision | Core |
| 🐛 Bug Report Generator | Failure analysis → Word/Jira bug reports | Core |
| 🧠 RAG Knowledge Base | Semantic search over your standards & docs | Enhanced |
| 📊 Dashboard | Coverage analytics & session history | Enhanced |

---

## 🚀 Quick Start

### Option A — Local Python (recommended for development)

```bash
# 1. Clone the project
git clone <your-repo-url>
cd AI_QA_Copilot

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY or OPENAI_API_KEY

# 5. Run the app
streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

### Option B — Docker (recommended for demos)

```bash
# 1. Copy and configure .env
cp .env.example .env
# Edit .env — add your API key

# 2. Build and run
docker compose up --build

# App is at http://localhost:8501
```

---

## ⚙️ Configuration

Edit the sidebar in the app to select your LLM provider and enter your API key, or set environment variables in `.env`:

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic Claude API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `OLLAMA_BASE_URL` | Ollama local server URL (default: http://localhost:11434) |

---

## 📁 Project Structure

```
AI_QA_Copilot/
├── app.py                   # Streamlit entry point
├── config.py                # Configuration
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
│
├── agents/                  # AI agent modules
│   ├── requirement_agent.py # Requirements → test cases
│   ├── automation_agent.py  # Test cases → code
│   ├── api_agent.py         # OpenAPI → API tests
│   ├── log_agent.py         # Log → root cause analysis
│   └── bug_agent.py         # Failure → bug report
│
├── services/                # Shared services
│   ├── llm.py               # LLM abstraction (Claude/OpenAI/Ollama)
│   ├── rag.py               # ChromaDB RAG service
│   ├── parser.py            # Document parsing (PDF/DOCX/TXT)
│   └── export.py            # Excel/Word/ZIP export
│
├── pages/                   # Streamlit UI pages
│   ├── home.py
│   ├── test_case_gen.py
│   ├── automation_gen.py
│   ├── api_test_gen.py
│   ├── log_analyser.py
│   ├── screenshot_analyser.py
│   ├── bug_report.py
│   ├── rag_kb.py
│   └── dashboard.py
│
├── utils/                   # Utility helpers
│   ├── session.py           # Streamlit session state
│   ├── file_helpers.py      # File I/O
│   └── formatting.py        # UI formatting
│
├── prompts/                 # Prompt templates (editable)
│   ├── requirement_prompts.py
│   └── log_prompts.py
│
├── knowledge/               # Seed knowledge base content
│   └── qa_standards.py
│
└── templates/               # Sample files for demo
    ├── sample_requirements.txt
    ├── sample_api_spec.yaml
    └── sample_log.txt
```

---

## 🔌 Supported LLM Providers

| Provider | Models | Best For |
|---|---|---|
| **Anthropic Claude** | claude-sonnet-4-6 | Long docs, log analysis, code gen |
| **OpenAI GPT-4** | gpt-4o, gpt-4-turbo | Vision (screenshots), code gen |
| **Ollama (Local)** | llama3.2, mistral | Offline demos, no API cost |

---

## 📦 Key Dependencies

```
streamlit        — UI framework
anthropic        — Claude API
openai           — GPT-4 API
chromadb         — Vector database for RAG
pdfplumber       — PDF parsing
python-docx      — DOCX parsing & export
openpyxl         — Excel export
plotly           — Interactive charts
PyYAML           — OpenAPI spec parsing
```

---

## 🗺️ Roadmap

- [x] Core test case generation
- [x] Playwright / Selenium / Pytest code generation
- [x] OpenAPI → API test suite
- [x] Log root cause analysis (incl. MQTT, KNX, BACnet, Modbus)
- [x] Screenshot defect detection
- [x] Bug report generation (Word + Jira format)
- [x] RAG knowledge base (ChromaDB)
- [x] Dashboard analytics
- [ ] Jira REST API live ticket creation
- [ ] GitHub/GitLab issue integration
- [ ] Smart regression selector (code diff → test subset)
- [ ] Multi-user authentication
- [ ] Appium mobile test generation

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
