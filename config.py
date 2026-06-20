"""
Configuration and environment management for AI QA Copilot
"""
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Config:
    # ── Directories ────────────────────────────────────────────────
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent)
    uploads_dir: Path = field(default_factory=lambda: Path("uploads"))
    reports_dir: Path = field(default_factory=lambda: Path("reports"))
    automation_dir: Path = field(default_factory=lambda: Path("automation"))
    knowledge_dir: Path = field(default_factory=lambda: Path("knowledge"))
    chroma_dir: Path = field(default_factory=lambda: Path(".chroma_db"))

    # ── LLM Defaults ───────────────────────────────────────────────
    default_provider: str = "Claude (Anthropic)"
    anthropic_model: str = "claude-sonnet-4-6"
    openai_model: str = "gpt-4o"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # ── API Keys (from env) ────────────────────────────────────────
    anthropic_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", "")
    )
    openai_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")
    )

    # ── Chunking / RAG ────────────────────────────────────────────
    chunk_size: int = 1500
    chunk_overlap: int = 200
    rag_top_k: int = 5
    max_log_chars: int = 60_000   # chars sent to LLM from logs

    # ── Output ────────────────────────────────────────────────────
    max_test_cases: int = 50

    def ensure_dirs(self):
        for d in [self.uploads_dir, self.reports_dir,
                  self.automation_dir, self.knowledge_dir]:
            Path(d).mkdir(parents=True, exist_ok=True)


config = Config()
config.ensure_dirs()
