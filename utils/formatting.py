"""
Formatting Utilities — shared UI formatting helpers
"""


def severity_badge_html(severity: str) -> str:
    colors = {
        "Critical": ("#FF0000", "white"),
        "High":     ("#FF6B35", "white"),
        "Medium":   ("#F6AD55", "#333"),
        "Low":      ("#68D391", "#333"),
        "CRITICAL": ("#FF0000", "white"),
        "HIGH":     ("#FF6B35", "white"),
        "MEDIUM":   ("#F6AD55", "#333"),
        "LOW":      ("#68D391", "#333"),
    }
    bg, fg = colors.get(severity, ("#A0AEC0", "white"))
    return (
        f'<span style="background:{bg};color:{fg};padding:2px 8px;'
        f'border-radius:10px;font-size:0.78rem;font-weight:bold;">{severity}</span>'
    )


def priority_badge_html(priority: str) -> str:
    colors = {
        "P1": ("#FF0000", "white"),
        "P2": ("#FF6B35", "white"),
        "P3": ("#F6AD55", "#333"),
        "P4": ("#68D391", "#333"),
    }
    bg, fg = colors.get(priority, ("#A0AEC0", "white"))
    return (
        f'<span style="background:{bg};color:{fg};padding:2px 8px;'
        f'border-radius:10px;font-size:0.78rem;font-weight:bold;">{priority}</span>'
    )


def confidence_icon(level: str) -> str:
    return {"High": "🟢", "Medium": "🟡", "Low": "🔴"}.get(level, "⚪")


def priority_icon(priority: str) -> str:
    return {
        "Critical": "🔴",
        "High":     "🟠",
        "Medium":   "🟡",
        "Low":      "🟢",
    }.get(priority, "⚪")


def truncate(text: str, max_len: int = 80) -> str:
    return text[:max_len] + "…" if len(text) > max_len else text


def format_steps(steps) -> str:
    """Format a list of steps as a numbered string."""
    if isinstance(steps, list):
        return "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))
    return str(steps)


def tag_pills_html(tags: list[str]) -> str:
    pills = "".join(
        f'<span style="background:#EBF4FF;color:#2B6CB0;padding:2px 7px;'
        f'border-radius:8px;font-size:0.75rem;margin-right:4px;">{t}</span>'
        for t in tags
    )
    return pills
