"""
File Utilities — save/load generated artefacts to disk
"""
import json
import os
from datetime import datetime
from pathlib import Path


REPORTS_DIR = Path("reports")
AUTOMATION_DIR = Path("automation")
UPLOADS_DIR = Path("uploads")


def _ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_test_cases(test_cases: list, name: str = "") -> Path:
    """Save test cases JSON to reports directory."""
    REPORTS_DIR.mkdir(exist_ok=True)
    slug = name.replace(" ", "_").lower()[:30] if name else "test_cases"
    path = REPORTS_DIR / f"{slug}_{_ts()}.json"
    path.write_text(json.dumps(test_cases, indent=2, ensure_ascii=False))
    return path


def save_code(code: str, filename: str) -> Path:
    """Save generated automation code to automation directory."""
    AUTOMATION_DIR.mkdir(exist_ok=True)
    path = AUTOMATION_DIR / filename
    path.write_text(code, encoding="utf-8")
    return path


def save_bug_report(report: dict) -> Path:
    """Save bug report JSON to reports directory."""
    REPORTS_DIR.mkdir(exist_ok=True)
    bug_id = report.get("bug_id", "BUG").replace("-", "_")
    path = REPORTS_DIR / f"{bug_id}_{_ts()}.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return path


def list_reports() -> list[dict]:
    """List all files in the reports directory."""
    REPORTS_DIR.mkdir(exist_ok=True)
    files = []
    for f in sorted(REPORTS_DIR.iterdir(), reverse=True):
        if f.is_file():
            files.append({
                "name": f.name,
                "size_kb": round(f.stat().st_size / 1024, 1),
                "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                "path": str(f),
            })
    return files


def list_automation() -> list[dict]:
    """List all files in the automation directory."""
    AUTOMATION_DIR.mkdir(exist_ok=True)
    files = []
    for f in sorted(AUTOMATION_DIR.iterdir(), reverse=True):
        if f.is_file():
            files.append({
                "name": f.name,
                "size_kb": round(f.stat().st_size / 1024, 1),
                "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                "path": str(f),
            })
    return files


def read_file(path: str) -> str:
    """Read a file from disk."""
    return Path(path).read_text(encoding="utf-8", errors="replace")


def delete_file(path: str) -> bool:
    """Delete a file from disk."""
    try:
        Path(path).unlink()
        return True
    except Exception:
        return False
