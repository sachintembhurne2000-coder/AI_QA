"""Screenshot Analyser page"""
import streamlit as st
import base64
import json
from services.llm import call_llm, extract_json, get_llm_config
from services.export import to_json_bytes


SCREENSHOT_SYSTEM = """You are a senior UI/UX QA engineer expert in detecting visual defects,
accessibility issues, and functional problems from screenshots.
Analyse screenshots thoroughly and provide detailed, actionable defect reports.
Always respond with JSON only.
"""

SCREENSHOT_PROMPT = """Analyse this UI screenshot and identify:
1. Any UI defects, visual bugs, or layout issues
2. Missing or incorrect elements
3. Text/content errors (truncation, overflow, wrong text)
4. Colour or contrast issues
5. Accessibility concerns
6. Console errors or error messages visible
7. Overall UI health score (0-100)

Respond as JSON:
{{
  "ui_health_score": 85,
  "overall_assessment": "Brief 2-3 sentence assessment",
  "defects": [
    {{
      "id": "D-001",
      "severity": "Critical | High | Medium | Low",
      "category": "Layout | Colour | Text | Missing Element | Error | Accessibility | Functionality",
      "description": "Clear description of the defect",
      "location": "Where on the screen (e.g., top-right, navigation bar)",
      "expected": "What should be there",
      "actual": "What is actually shown",
      "impact": "User impact of this defect"
    }}
  ],
  "visible_text_extracted": "All visible text found via OCR",
  "positive_observations": ["things that look correct"],
  "recommendations": ["specific fix recommendations"]
}}
"""


def _encode_image(image_bytes: bytes, mime: str) -> str:
    return base64.standard_b64encode(image_bytes).decode("utf-8")


def analyse_screenshot_anthropic(image_bytes: bytes, mime: str, api_key: str, model: str) -> dict:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        b64 = _encode_image(image_bytes, mime)
        msg = client.messages.create(
            model=model,
            max_tokens=2048,
            system=SCREENSHOT_SYSTEM,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": mime, "data": b64}},
                    {"type": "text", "text": SCREENSHOT_PROMPT},
                ],
            }],
        )
        return extract_json(msg.content[0].text)
    except Exception as e:
        raise ValueError(f"Vision analysis error: {e}")


def analyse_screenshot_openai(image_bytes: bytes, mime: str, api_key: str, model: str) -> dict:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        b64 = _encode_image(image_bytes, mime)
        resp = client.chat.completions.create(
            model=model,
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                    {"type": "text", "text": SCREENSHOT_SYSTEM + "\n\n" + SCREENSHOT_PROMPT},
                ],
            }],
        )
        return extract_json(resp.choices[0].message.content)
    except Exception as e:
        raise ValueError(f"Vision analysis error: {e}")


def render():
    st.markdown("""
    <div class="main-header">
        <h1>🖼️ Screenshot Analyser</h1>
        <p>Upload UI screenshots → AI detects defects, layout issues, and missing elements</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Upload ───────────────────────────────────────────────────────────────
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded = st.file_uploader(
            "Upload screenshot",
            type=["png", "jpg", "jpeg", "webp"],
            help="Upload a PNG or JPEG screenshot of your application UI",
        )
    with col2:
        st.markdown("**Analysis Options**")
        check_accessibility = st.checkbox("Check accessibility", value=True)
        check_ocr = st.checkbox("Extract visible text (OCR)", value=True)
        severity_filter = st.multiselect(
            "Show severities",
            ["Critical", "High", "Medium", "Low"],
            default=["Critical", "High", "Medium", "Low"],
        )

    if uploaded:
        image_bytes = uploaded.read()
        mime = f"image/{uploaded.name.split('.')[-1].lower()}"
        if mime == "image/jpg":
            mime = "image/jpeg"

        # Display image
        st.image(image_bytes, caption=uploaded.name, use_column_width=True)

        analyse_btn = st.button("🔍 Analyse Screenshot", type="primary")

        if analyse_btn:
            cfg = get_llm_config()
            if not cfg["api_key"] and cfg["provider"] != "Ollama (Local)":
                st.error("Please configure your API key in the sidebar.")
                return

            with st.spinner("🤖 Analysing screenshot with AI Vision... (10-20 seconds)"):
                try:
                    if "Claude" in cfg["provider"]:
                        result = analyse_screenshot_anthropic(
                            image_bytes, mime, cfg["api_key"], cfg["model"]
                        )
                    elif "OpenAI" in cfg["provider"]:
                        result = analyse_screenshot_openai(
                            image_bytes, mime, cfg["api_key"], cfg["model"]
                        )
                    else:
                        st.warning("Screenshot analysis requires Claude or OpenAI (vision model). Ollama vision support varies.")
                        return

                    st.session_state["screenshot_analysis"] = result
                except Exception as e:
                    st.error(f"Analysis error: {e}")
                    return

    if "screenshot_analysis" in st.session_state:
        result = st.session_state["screenshot_analysis"]
        st.markdown("---")
        st.subheader("📊 Analysis Results")

        # Health score
        score = result.get("ui_health_score", 0)
        score_color = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
        col1, col2, col3 = st.columns(3)
        col1.metric("🏥 UI Health Score", f"{score}/100", delta=f"{score_color}")
        defects = result.get("defects", [])
        filtered = [d for d in defects if d.get("severity") in severity_filter]
        col2.metric("🐛 Total Defects", len(defects))
        critical = sum(1 for d in defects if d.get("severity") == "Critical")
        col3.metric("🔴 Critical Defects", critical)

        # Overall assessment
        st.info(f"**Assessment:** {result.get('overall_assessment', '')}")

        # Defects
        if filtered:
            st.subheader(f"🐛 Defects Found ({len(filtered)})")
            for defect in filtered:
                sev = defect.get("severity", "Low")
                icon = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(sev, "⚪")
                with st.expander(f"{icon} [{sev}] {defect.get('id', '')} — {defect.get('description', '')[:80]}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Category:** {defect.get('category', '')}")
                        st.markdown(f"**Location:** {defect.get('location', '')}")
                        st.markdown(f"**Impact:** {defect.get('impact', '')}")
                    with col2:
                        st.markdown(f"**Expected:** {defect.get('expected', '')}")
                        st.markdown(f"**Actual:** {defect.get('actual', '')}")

        # Positive observations
        positives = result.get("positive_observations", [])
        if positives:
            st.subheader("✅ Positive Observations")
            for p in positives:
                st.markdown(f"- {p}")

        # Extracted text
        if check_ocr and result.get("visible_text_extracted"):
            with st.expander("📝 Extracted Text (OCR)"):
                st.text(result["visible_text_extracted"])

        # Recommendations
        recs = result.get("recommendations", [])
        if recs:
            st.subheader("💡 Recommendations")
            for r in recs:
                st.markdown(f"- {r}")

        # Export
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📋 Export Analysis (JSON)",
                data=to_json_bytes(result),
                file_name="screenshot_analysis.json",
                mime="application/json",
                use_container_width=True,
            )
        with col2:
            if st.button("🐛 Generate Bug Report from Defects", use_container_width=True):
                st.session_state["bug_from_screenshot"] = result
                st.success("Navigate to 🐛 Bug Report Generator")
    else:
        if not uploaded:
            st.info("👆 Upload a screenshot to begin analysis.")
