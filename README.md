# Smart P&ID Query Engine — Multimodal GraphRAG Digital Twin

> **Built during my internship at Indian Oil Corporation Limited (IOCL), Guwahati.**  
> A production-grade AI system that lets plant engineers query complex Piping & Instrumentation Diagrams (P&IDs) and Standard Operating Procedures using natural language.

---

## What It Does

Traditional plant operations require engineers to manually search through 500-page SOPs and visually trace P&ID blueprints to find equipment specs or pipeline connections — a slow, error-prone process.

This system replaces that with a **hybrid AI pipeline** that:

1. **Reads any P&ID blueprint** using Computer Vision (OpenCV + Tesseract OCR with preprocessing) to extract and geolocate equipment tags (pumps, valves, sensors, etc.)
2. **Answers "what connects to what"** using a Knowledge Graph (NetworkX DiGraph) that encodes pipeline topology with deterministic precision — no hallucination possible on flow queries
3. **Answers "what does this equipment do"** using Retrieval-Augmented Generation (RAG) over indexed SOPs via ChromaDB vector search
4. **Streams answers in real time** using a multimodal LLM (LLaVA-Phi3 for visual context, Llama2 as text fallback) via Ollama, with Server-Sent Events so responses appear token-by-token

---

## Architecture

```
User Question
     │
     ├─► Intent Check (casual? → lightweight conversational path)
     │
     ├─► Embed question (nomic-embed-text, 768-dim)
     │       └─► ChromaDB HNSW search → top-3 SOP chunks
     │
     ├─► Regex tag detection → NetworkX DiGraph traversal
     │       └─► Upstream/downstream topology string
     │
     └─► Build prompt → LLaVA-Phi3 (with image) / Llama2 (text-only)
                └─► SSE stream → browser renders tokens in real-time
```

**Why GraphRAG?** A vector database finds *what* equipment does. A knowledge graph finds *how things connect*. This system uses both, injecting graph topology and SOP chunks into a structured prompt that forces the LLM to use factual data rather than guess.

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend API | Flask + Flask-CORS | Lightweight REST server |
| Computer Vision | OpenCV, Tesseract OCR | Blueprint tag extraction with preprocessing pipeline |
| Knowledge Graph | NetworkX DiGraph | Deterministic flow tracing (predecessors/successors) |
| Embeddings | nomic-embed-text (via Ollama) | Local, free, 768-dim semantic embeddings |
| Vector Store | ChromaDB (HNSW index) | Persistent vector search, O(log n) retrieval |
| LLM Orchestration | LangChain | Chunking, retrieval, LLM abstraction |
| Text LLM | Llama2 7B (via Ollama) | Local inference, temperature=0.2 for factual answers |
| Vision LLM | LLaVA-Phi3 (via Ollama) | Multimodal: reads blueprint image + text context |
| Frontend | Vanilla JS + CSS | SSE-based streaming chat, no framework needed |

---

## Key Engineering Decisions

- **`temperature=0.2`**: Safety-critical queries need deterministic answers. Low temperature sharpens the LLM's probability distribution, near-eliminating creative variation.
- **Preprocessing before OCR**: Raw blueprint images fail Tesseract on low contrast. Added 5-step pipeline: grayscale → upscale → CLAHE → denoise → adaptive threshold. Tag detection improved significantly on dark/noisy images.
- **Graph for topology, RAG for docs**: Vector databases return semantically similar text — they can't answer "what feeds into HX-211?" A directed graph with `predecessors()`/`successors()` gives exact, deterministic answers.
- **Streaming (SSE)**: `stream=False` on Ollama made users wait 30-60 seconds for any response. Switching to Server-Sent Events with a `ReadableStream` frontend shows the first token in ~3 seconds.
- **`INSUFFICIENT DATA` fallback**: The prompt instructs the LLM to respond with a safe error message rather than guess when neither the topology map nor documentation contains the answer.

---

## Setup

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai) installed and running
- [Tesseract-OCR](https://github.com/UB-Mannheim/tesseract/wiki) installed

### Installation

```bash
# 1. Clone and enter the repo
git clone https://github.com/YOUR_USERNAME/graphrag-pid-digital-twin
cd graphrag-pid-digital-twin

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Pull required Ollama models (one-time, ~8GB total)
ollama pull llama2
ollama pull llava-phi3
ollama pull nomic-embed-text

# 5. Run the backend
python app_professional.py

# 6. Open index_professional.html in your browser
```

### Configuration (optional)

Override any setting via environment variable:

```bash
export DEBUG=true
export OLLAMA_TEXT_MODEL=mistral   # swap the text model
export PORT=8080
```

---

## Project Structure

```
├── app.py                  # Main backend: CV pipeline + GraphRAG + Graph API + SSE streaming
├── index.html              # Frontend: real-time streaming chat UI
├── requirements.txt        # All Python dependencies (pinned versions)
├── verify_system.py        # Pre-flight system check (run before first launch)
├── create_demo_files.py    # Generates sample P&ID + SOP files for testing
├── test_vision.py          # Standalone OCR/vision pipeline test script
│
├── QUICKSTART.md           # Fastest path to a running system
├── SETUP.md                # Detailed installation instructions
├── ADVANCED.md             # Advanced configuration and customisation
├── TROUBLESHOOTING.md      # Common errors and fixes
├── START_HERE.md           # Orientation guide for new contributors
├── FILE_INVENTORY.md       # Description of every file in the project
│
├── uploads/                # Uploaded blueprint images (gitignored, auto-created)
└── chroma_db/              # ChromaDB vector store (gitignored, auto-created at runtime)
```

---

## What I Learned

This project taught me that production AI systems are **not just about the model** — they're about the architecture around it. The LLM is the last 10% of the work. The remaining 90% is data pipelines, retrieval quality, fallback behaviour, latency management, and knowing when to use deterministic logic instead of generative AI.

---

*Internship Project — IOCL Guwahati Refinery | 2026*
