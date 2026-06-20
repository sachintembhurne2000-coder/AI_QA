"""RAG Knowledge Base management page"""
import streamlit as st
import pandas as pd
from services.parser import parse_document
from services.rag import add_document, list_sources, delete_source, get_stats, query


DOC_TYPES = [
    "requirements",
    "test_strategy",
    "coding_standards",
    "sop",
    "api_documentation",
    "known_bugs",
    "architecture",
    "general",
]


def render():
    st.markdown("""
    <div class="main-header">
        <h1>🧠 RAG Knowledge Base</h1>
        <p>Build a semantic knowledge base that AI agents use for context-aware generation</p>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    stats = get_stats()
    col1, col2 = st.columns(2)
    col1.metric("📚 Total Chunks", stats.get("total_chunks", 0))
    col2.metric("📄 Total Sources", stats.get("total_sources", 0))

    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["➕ Add Documents", "📋 Browse Sources", "🔍 Search KB"])

    # ── Tab 1: Add ────────────────────────────────────────────────────────────
    with tab1:
        st.subheader("Add Document to Knowledge Base")

        col1, col2 = st.columns([2, 1])
        with col1:
            uploaded = st.file_uploader(
                "Upload document",
                type=["pdf", "docx", "txt", "md", "yaml", "json"],
                accept_multiple_files=True,
                key="kb_upload",
            )
        with col2:
            doc_type = st.selectbox("Document Type", DOC_TYPES)
            st.caption("This helps the AI filter relevant context")

        text_input = st.text_area(
            "— or paste text directly —",
            height=200,
            placeholder="Paste requirements, SOPs, standards, known issues...",
            key="kb_paste",
        )
        manual_name = st.text_input("Source name (for pasted text)", placeholder="test_strategy_v2")

        add_btn = st.button("➕ Add to Knowledge Base", type="primary")

        if add_btn:
            docs_added = 0

            # Process uploaded files
            if uploaded:
                for f in uploaded:
                    with st.spinner(f"Processing {f.name}..."):
                        try:
                            text = parse_document(f, f.name)
                            n = add_document(text, f.name, doc_type)
                            st.success(f"✅ Added **{f.name}** — {n} chunks")
                            docs_added += 1
                        except Exception as e:
                            st.error(f"Error adding {f.name}: {e}")

            # Process pasted text
            if text_input.strip():
                name = manual_name.strip() or "pasted_document"
                with st.spinner(f"Processing {name}..."):
                    try:
                        n = add_document(text_input, name, doc_type)
                        st.success(f"✅ Added **{name}** — {n} chunks")
                        docs_added += 1
                    except Exception as e:
                        st.error(f"Error: {e}")

            if docs_added == 0 and not uploaded and not text_input.strip():
                st.warning("Please upload a file or paste text.")

        # Pre-built knowledge
        st.markdown("---")
        st.subheader("💡 Seed with Example Knowledge")
        st.caption("Add pre-built QA knowledge to improve AI outputs")

        seeds = {
            "QA Best Practices": {
                "text": """QA Best Practices and Testing Standards:
1. Every test case must have a unique ID, clear title, preconditions, numbered steps, and expected result.
2. Test coverage should include: happy path, negative paths, boundary values, and edge cases.
3. Priority levels: Critical (blocking), High (major feature), Medium (standard), Low (cosmetic).
4. Bug reports must include: reproduction steps, actual vs expected, environment, severity, and priority.
5. Regression suites should be maintained and run on every build.
6. API tests must cover: 2xx success, 4xx client errors, 5xx server errors, auth scenarios, and rate limits.
7. UI tests should use stable locators: prefer data-testid > aria > id > CSS > XPath.
8. Performance baselines: page load < 3s, API response < 500ms for 95th percentile.
""",
                "type": "test_strategy",
            },
            "Embedded Protocol Guidelines": {
                "text": """Embedded Systems and Protocol Testing Guidelines:
MQTT Testing:
- Verify QoS levels (0, 1, 2) for message delivery guarantees
- Test broker connection, reconnection, and timeout scenarios
- Validate topic hierarchy and wildcard subscriptions
- Check retained message behaviour and LWT (Last Will Testament)

KNX Testing:
- Validate group address assignments and telegram routing
- Test ETS configuration import/export
- Verify KNX/IP gateway communication
- Check DPT (Data Point Types) conversions

BACnet Testing:
- Test object property read/write operations
- Validate COV (Change of Value) subscriptions
- Check WhoIs/IAm device discovery
- Test scheduling and trending functions

Modbus Testing:
- Validate function codes: 01-06, 15-16
- Test register read/write with correct data types
- Check exception code handling
- Verify byte order (Big/Little endian)
""",
                "type": "sop",
            },
        }

        col1, col2 = st.columns(2)
        for i, (name, data) in enumerate(seeds.items()):
            with (col1 if i % 2 == 0 else col2):
                if st.button(f"➕ Add: {name}", use_container_width=True, key=f"seed_{i}"):
                    with st.spinner(f"Adding {name}..."):
                        try:
                            n = add_document(data["text"], name, data["type"])
                            st.success(f"✅ Added {n} chunks")
                        except Exception as e:
                            st.error(f"Error: {e}")

    # ── Tab 2: Browse ─────────────────────────────────────────────────────────
    with tab2:
        st.subheader("Knowledge Base Sources")
        sources = list_sources()

        if not sources:
            st.info("No documents in knowledge base yet. Add documents in the 'Add Documents' tab.")
        else:
            df = pd.DataFrame(sources)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.subheader("🗑️ Delete Source")
            source_names = [s["source"] for s in sources]
            to_delete = st.selectbox("Select source to delete", source_names)
            if st.button("🗑️ Delete Selected Source", type="secondary"):
                n = delete_source(to_delete)
                st.success(f"Deleted {n} chunks from '{to_delete}'")
                st.rerun()

    # ── Tab 3: Search ─────────────────────────────────────────────────────────
    with tab3:
        st.subheader("🔍 Semantic Search")
        query_text = st.text_input("Search query", placeholder="How should we test MQTT QoS levels?")
        n_results = st.slider("Number of results", 1, 10, 5)

        if st.button("🔍 Search", type="primary") and query_text:
            results = query(query_text, n_results)
            if results:
                st.success(f"Found {len(results)} results")
                for r in results:
                    with st.expander(f"📄 {r['source']} (relevance: {r['score']:.2%})"):
                        st.markdown(f"**Type:** {r['type']}")
                        st.text(r["text"][:500] + "..." if len(r["text"]) > 500 else r["text"])
            else:
                st.warning("No results found. Try adding more documents or a different query.")
