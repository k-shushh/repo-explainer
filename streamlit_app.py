from rag_pipeline import create_vectorstore
import streamlit as st
from dotenv import load_dotenv

from llm_utils import get_chat_model

load_dotenv()

st.set_page_config(
    page_title="repo-explainer",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Design system: dark editor palette, monospace accents ----------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

    #MainMenu, footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: #0f1117;
    }

    .block-container {
        padding-top: 1.5rem;
        max-width: 880px;
    }

    /* ---- window chrome bar (the signature element) ---- */
    .term-bar {
        display: flex;
        align-items: center;
        gap: 8px;
        background: #171a21;
        border: 1px solid #262a35;
        border-radius: 10px 10px 0 0;
        padding: 10px 14px;
        margin-top: 4px;
    }
    .term-dot {
        width: 11px; height: 11px; border-radius: 50%;
    }
    .term-bar .term-path {
        margin-left: 10px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: #8b92a4;
    }
    .term-body {
        background: #12141b;
        border: 1px solid #262a35;
        border-top: none;
        border-radius: 0 0 10px 10px;
        padding: 26px 30px 10px 30px;
        margin-bottom: 22px;
    }

    .app-eyebrow {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #f5a623;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .app-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.7rem;
        font-weight: 700;
        color: #e6e8eb;
        margin-bottom: 4px;
    }
    .app-title span { color: #f5a623; }
    .app-subtitle {
        color: #8b92a4;
        font-size: 0.92rem;
        margin-bottom: 4px;
    }

    /* ---- status pill ---- */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-family: 'JetBrains Mono', monospace;
        padding: 4px 10px;
        border-radius: 5px;
        font-size: 0.75rem;
        font-weight: 500;
        border: 1px solid #262a35;
    }
    .status-ready { color: #7ee787; }
    .status-empty { color: #8b92a4; }
    .status-dot { width: 7px; height: 7px; border-radius: 50%; background: currentColor; }

    /* ---- sidebar ---- */
    section[data-testid="stSidebar"] {
        background: #12141b;
        border-right: 1px solid #262a35;
    }
    section[data-testid="stSidebar"] h3 {
        font-family: 'JetBrains Mono', monospace;
        color: #e6e8eb;
        font-size: 0.95rem;
    }
    section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] p {
        color: #6b7280 !important;
    }

    /* ---- inputs & buttons ---- */
    div[data-testid="stFormSubmitButton"] button,
    section[data-testid="stSidebar"] div[data-testid="stButton"] button {
    background: #f5a623 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #f5a623 !important;
        box-shadow: 0 0 0 1px #f5a623 !important;
    }
    div[data-testid="stFormSubmitButton"] button,
    section[data-testid="stSidebar"] div[data-testid="stButton"] button {
        background: #f5a623 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
    }
    div[data-testid="stFormSubmitButton"] button:hover,
    section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover {
        background: #ffb84d !important;
    }

    /* ---- empty state ---- */
    .empty-state {
        text-align: center;
        padding: 50px 20px 30px 20px;
        color: #6b7280;
    }
    .empty-state .glyph {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.6rem;
        color: #262a35;
        margin-bottom: 10px;
    }
    .empty-state h3 {
        font-family: 'JetBrains Mono', monospace;
        color: #e6e8eb;
        font-size: 1rem;
        margin-bottom: 6px;
        font-weight: 600;
    }
    .empty-state p { font-size: 0.88rem; }

    /* ---- chat ---- */
    div[data-testid="stChatMessage"] {
        background: transparent !important;
        border: none !important;
        padding: 6px 0 !important;
    }
    .prompt-symbol {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        margin-right: 6px;
    }
    .prompt-symbol.user { color: #7ee787; }
    .prompt-symbol.assistant { color: #f5a623; }

    div[data-testid="stChatInput"] textarea {
        color: #e6e8eb !important;
        border: 1px solid #262a35 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.88rem !important;
    }
    div[data-testid="stChatInput"] {
        border-top: 1px solid #262a35 !important;
    }

    .source-ref {
        border-left: 2px solid #f5a623;
        padding-left: 10px;
        margin-bottom: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #8b92a4;
    }

    
    [data-testid="InputInstructions"] {
        display: none !important;
    }

    div[data-testid="stChatInput"] textarea::placeholder {
        background: transparent !important;
        opacity: 1 !important;
    }

    div[data-testid="stChatInput"] textarea:focus {
        box-shadow: none !important;
        outline: none !important;
    }

    hr { border-color: #262a35 !important; }
    </style>
""", unsafe_allow_html=True)

# ---------- Session state ----------
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "repo_loaded" not in st.session_state:
    st.session_state.repo_loaded = False
if "repo_name" not in st.session_state:
    st.session_state.repo_name = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- Sidebar: repo setup ----------
with st.sidebar:
    st.markdown("### repository")

    if st.session_state.repo_loaded:
        st.markdown(
            f'<span class="status-pill status-ready"><span class="status-dot"></span>{st.session_state.repo_name}</span>',
            unsafe_allow_html=True
        )
        st.write("")
        if st.button("switch repository", use_container_width=True):
            st.session_state.repo_loaded = False
            st.session_state.vectorstore = None
            st.session_state.messages = []
            st.rerun()
    else:
        st.markdown('<span class="status-pill status-empty"><span class="status-dot"></span>no repo loaded</span>', unsafe_allow_html=True)
        st.write("")
        with st.form("repo_form", clear_on_submit=False, border=False):
            repo_url = st.text_input(
                "GitHub URL",
                placeholder="github.com/user/repo",
                label_visibility="collapsed"
            )
            submitted = st.form_submit_button("clone & index", use_container_width=True)

        if submitted:
            if not repo_url.strip():
                st.error("enter a repository URL")
            else:
                try:
                    with st.spinner("cloning repo, building embeddings..."):
                        st.session_state.vectorstore = create_vectorstore(repo_url)
                        st.session_state.repo_loaded = True
                        st.session_state.repo_name = repo_url.rstrip("/").split("/")[-1]
                    st.rerun()
                except Exception as e:
                    st.error(f"failed to load: {e}")

    st.divider()
    st.caption("RAG over any public GitHub repo · LLaMA 3.1 via Groq")

# ---------- Main: window chrome + header ----------
path_label = f"~/{st.session_state.repo_name}" if st.session_state.repo_loaded else "~/repo-explainer"
st.markdown(f"""
    <div class="term-bar">
        <span class="term-dot" style="background:#ff5f56;"></span>
        <span class="term-dot" style="background:#ffbd2e;"></span>
        <span class="term-dot" style="background:#27c93f;"></span>
        <span class="term-path">{path_label}</span>
    </div>
    <div class="term-body">
        <div class="app-eyebrow">code search</div>
        <div class="app-title">repo<span>-</span>explainer</div>
        <div class="app-subtitle">Ask questions about a codebase's structure, logic, and implementation.</div>
    </div>
""", unsafe_allow_html=True)

# ---------- Main: chat ----------
if not st.session_state.repo_loaded:
    st.markdown(
        '<div class="empty-state">'
        '<div class="glyph">&lt;/&gt;</div>'
        '<h3>no repository loaded</h3>'
        '<p>paste a GitHub URL in the sidebar to start exploring the codebase</p>'
        '</div>',
        unsafe_allow_html=True
    )
else:
    for msg in st.session_state.messages:
        avatar = "🧑‍💻" if msg["role"] == "user" else "💡"
        symbol_class = "user" if msg["role"] == "user" else "assistant"
        symbol = "$" if msg["role"] == "user" else ">"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(
                f'<span class="prompt-symbol {symbol_class}">{symbol}</span>{msg["content"]}',
                unsafe_allow_html=True
            )
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander("source references"):
                    for i, src in enumerate(msg["sources"], 1):
                        st.markdown(f'<div class="source-ref">ref {i:02d}</div>', unsafe_allow_html=True)
                        st.code(src, language="python")

    question = st.chat_input("ask a question about this repo...")

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(f'<span class="prompt-symbol user">$</span>{question}', unsafe_allow_html=True)

        with st.chat_message("assistant", avatar="💡"):
            with st.spinner("searching repository..."):
                try:
                    retriever = st.session_state.vectorstore.as_retriever()
                    docs = retriever.invoke(question)

                    if not docs:
                        answer = "No relevant code found for that question. Try rephrasing it."
                        sources = []
                    else:
                        context = "\n\n".join(doc.page_content for doc in docs)
                        prompt = f"""You are a helpful code assistant. Answer the question using ONLY the provided code context.

Rules:
- Explain in plain English, in prose or bullet points.
- Do NOT output JSON, YAML, or mimic any return format/schema you see inside the code context — that's what the CODE does, not how you should answer.
- Only include a code snippet if it directly helps illustrate the answer, and keep it short.
- If the context doesn't contain enough information to answer, say so plainly instead of guessing.

Context:
{context}

Question:
{question}"""
                        llm = get_chat_model()
                        response = llm.invoke(prompt)
                        answer = response.content
                        sources = [doc.page_content for doc in docs]

                    st.markdown(f'<span class="prompt-symbol assistant">&gt;</span>{answer}', unsafe_allow_html=True)
                    if sources:
                        with st.expander("source references"):
                            for i, src in enumerate(sources, 1):
                                st.markdown(f'<div class="source-ref">ref {i:02d}</div>', unsafe_allow_html=True)
                                st.code(src, language="python")

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                except Exception as e:
                    error_msg = f"Error: {e}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})
