# repo-explainer

RAG-powered Q&A over any public GitHub repository. Paste a repo URL, and ask questions about its structure, logic, and implementation — answers are grounded in the actual codebase, not general knowledge.

**Live demo:** https://k-shushh-repo-explainer-streamlit-app-hbny3d.streamlit.app/

## How it works

1. **Clone** — the target repo is cloned locally (`github_loader.py`)
2. **Load & chunk** — source files are parsed and split into chunks (`code_loader.py`, `code_parser.py`)
3. **Embed & index** — chunks are embedded (HuggingFace embeddings) and stored in a Chroma vectorstore (`rag_pipeline.py`)
4. **Retrieve & answer** — on each question, the top relevant chunks are retrieved and passed as context to LLaMA 3.1 (via Groq) to generate a grounded answer

```
GitHub URL → clone → chunk → embed → Chroma vectorstore
                                            │
                             question → retrieve top-k chunks → LLaMA 3.1 (Groq) → answer
```

## Stack

- **UI**: Streamlit
- **Orchestration**: LangChain
- **LLM**: LLaMA 3.1 8B Instant via Groq API
- **Embeddings**: HuggingFace (`sentence-transformers`)
- **Vector store**: Chroma
- **Deployment**: Streamlit Community Cloud

## Run locally

```bash
git clone <this-repo>
cd RAGApp
python -m venv ragenv
ragenv\Scripts\activate      # Windows
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_key_here
```

```bash
streamlit run streamlit_app.py
```

Open the local URL Streamlit prints, paste a public GitHub repo URL in the sidebar, and start asking questions once it's indexed.

## Project structure

```
RAGApp/
├── streamlit_app.py    # main UI — chat-based Q&A interface
├── rag_pipeline.py      # builds the vectorstore (create_vectorstore)
├── github_loader.py     # clones the target repo
├── code_loader.py       # loads source files from the cloned repo
├── code_parser.py       # parses/splits code into chunks
├── app.py               # standalone debug script for quick pipeline testing
└── requirements.txt
```

## Limitations

- No cap yet on repo size — very large repos can be slow to clone and embed
- Vectorstore is rebuilt from scratch on every repo load (not cached across sessions)
- Retrieval is chunk-based, not AST-aware, so answers about cross-file logic can miss context

## Roadmap

- [ ] Cache vectorstore per repo URL to avoid re-embedding on reload
- [ ] Repo size/file-count limits with clear error messaging
- [ ] AST-aware chunking for more accurate code retrieval
- [ ] Basic retrieval eval set (sample Q&A pairs to track answer quality)
