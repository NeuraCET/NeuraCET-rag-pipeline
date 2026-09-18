# Drishti 2026 AI Kiosk Assistant — NeuraCET

[![Event](https://img.shields.io/badge/Event-Drishti%202026-gold.svg)](https://drishti.cet.ac.in)
[![Maintained by](https://img.shields.io/badge/Maintained%20by-NeuraCET-blue.svg)](#)
[![Model](https://img.shields.io/badge/LLM-Qwen%203.5%20(4B)-green.svg)](https://ollama.com/library/qwen3.5:4b)
[![Retrieval](https://img.shields.io/badge/Retrieval-Hybrid%20(BM25%20%2B%20Dense)-purple.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](#)

An intelligent, interactive, and offline-capable RAG (Retrieval-Augmented Generation) assistant built for the **Drishti 2026** tech fest at the **College of Engineering Trivandrum (CET)**. Running as an interactive kiosk, it provides real-time event schedules, workshop details, rules, coordinator contacts, and official 2026 festival posters with **zero hallucinations** and a cheerful, welcoming personality.

---

## 🌟 Key Highlights

- **Real-Time Token Streaming**: Words appear live on screen in real time with an authentic typewriter effect straight from the local LLM as tokens are generated.
- **Instant Screen Transition**: Seamlessly switches from the thinking screen to the answer view the instant prompt evaluation finishes (~15s), with zero timeouts.
- **Zero Hallucinations & Cheerful Tone**: Strictly grounded in official documents from `dataRAG/`. If information is not in official festival records, it warmly and cheerfully informs the user.
- **Smart 2026 Poster Gating**: Automatically displays official high-resolution posters in the right column for **Drishti 2026** events, while past editions (2024, 2022) and non-event queries safely show the interactive mascot fallback.
- **Hybrid Retrieval Pipeline**: Combines lexical BM25 keyword matching with cached dense semantic embeddings (`all-MiniLM-L6-v2`) for pinpoint recall.
- **Completely Local & Offline**: Powered by Ollama running `qwen3.5:4b` locally without requiring internet access or paid external API keys.

---

## 🏗️ Architecture

```text
                     ┌──────────────────────────────┐
                     │   Vite + React Kiosk UI      │
                     │   (http://localhost:5173)    │
                     └──────────────┬───────────────┘
                                    │  Server-Sent Events (SSE)
                                    ▼
                     ┌──────────────────────────────┐
                     │     FastAPI Backend API      │
                     │   (http://localhost:8000)    │
                     └───────┬──────────────┬───────┘
                             │              │
       Hybrid Retrieval Engine              │ Local LLM Inference
      ┌──────────────────────┴───────┐      │ (think: false, stream: true)
      ▼                              ▼      ▼
┌──────────────┐             ┌─────────────────────────┐
│ BM25 Lexical │             │   Ollama (qwen3.5:4b)   │
│  + Cached    │             │ (http://localhost:11434)│
│ Dense Embeds │             └─────────────────────────┘
└──────────────┘
      │
      ▼
┌────────────────────────────────────────────────────────┐
│                      Knowledge Base                    │
│  • dataRAG/combined_events.json (2026 Events)          │
│  • dataRAG/Drishti-26.pdf (2026 Schedule & Highlights) │
│  • dataRAG/ai_summit_data.pdf (AI Summit 2026)         │
│  • dataRAG/Drishti'24.docx.pdf (2024 Archive)          │
│  • dataRAG/drishti2022.docx (2022 Archive)             │
│  • posters/ (44 Official 2026 Event Posters)           │
└────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```text
NeuraCET-rag-pipeline/
├── dataRAG/                    # Official festival knowledge documents
│   ├── combined_events.json    # Drishti 2026 registered events & metadata
│   ├── Drishti-26.pdf          # Drishti 2026 overview & schedule
│   ├── ai_summit_data.pdf      # Drishti 2026 AI Summit talks & panels
│   ├── Drishti'24.docx.pdf     # Drishti 2024 historical records
│   └── drishti2022.docx        # Drishti 2022 historical records
├── posters/                    # Official Drishti 2026 festival poster images
│   └── poster_index.json       # Poster mapping metadata
├── src/                        # Python backend source code
│   ├── ingest.py               # Robust multi-format document parser & chunker
│   ├── poster_registry.py      # Strict 2026 poster matcher & past-year gate
│   ├── rag_engine.py           # Hybrid retrieval & Ollama streaming client
│   └── server.py               # FastAPI server (/posters, /api/ask-stream)
├── ui/                         # Kiosk frontend (Vite + React + Tailwind)
│   ├── src/components/kiosk/   # AnswerScreen, AskScreen, ThinkingScreen, etc.
│   ├── src/lib/assistant.ts    # SSE stream reader client
│   └── src/pages/Kiosk.tsx     # Dynamic state machine & transitions
├── .env.example                # Safe environment variable configuration template
├── pyproject.toml              # Python project metadata and dependencies
└── main.py                     # Unified full-stack supervisor & process manager
```

---

## 🚀 Installation & Setup

### 1. Prerequisites

Before setting up, ensure your system has the following tools installed:

- **Python 3.10+** (Python 3.11 or 3.12 recommended across all platforms)
- **Node.js 18+** & **npm** (Download from [nodejs.org](https://nodejs.org))
- **Ollama**: Download and install from [ollama.com](https://ollama.com) (Available for Windows, macOS, and Linux)
- **PDF Extraction (Cross-Platform)**:
  - Text extraction is powered by `pypdf` which is automatically installed via dependencies and works 100% out-of-the-box on **Windows**, **macOS**, and **Linux**.
  - *(Optional)* For advanced paragraph formatting using `pdftotext`:
    - **Windows**: `winget install -e --id Xpdf.poppler` or `choco install poppler`
    - **macOS**: `brew install poppler`
    - **Debian / Ubuntu / Mint**: `sudo apt update && sudo apt install -y poppler-utils`
    - **Arch Linux**: `sudo pacman -S poppler`

---

### 2. Clone the Repository

```bash
git clone https://github.com/NeuraCET/NeuraCET-rag-pipeline.git
cd NeuraCET-rag-pipeline
```

---

### 3. Pull the Qwen 3.5 4B Model

Ensure the Ollama service is running, then pull the lightweight 4B parameter model:

```bash
# Start Ollama service (if not already running)
ollama serve

# In another terminal / PowerShell window:
ollama pull qwen3.5:4b
```

---

### 4. Python Environment Setup

#### On Linux & macOS:
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install all backend dependencies
pip install -e .
```

#### On Windows (PowerShell or Command Prompt):
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment in PowerShell
.\.venv\Scripts\Activate.ps1

# (If running Command Prompt instead)
# .venv\Scripts\activate.bat

# Install all backend dependencies
pip install -e .
```

*(Optional alternative for fast installs: `uv venv && uv pip install -e .`)*

---

### 5. Frontend Setup

Navigate to the `ui/` directory and install the React/Vite dependencies:

```bash
cd ui
npm install
cd ..
```

---

### 6. Environment Configuration

Copy the sample environment template:

- **Linux & macOS**:
  ```bash
  cp .env.example .env
  ```
- **Windows (PowerShell)**:
  ```powershell
  Copy-Item .env.example .env
  ```
- **Windows (Command Prompt)**:
  ```cmd
  copy .env.example .env
  ```

The default values are configured for local execution and require no changes:

```env
# Ollama service endpoint
OLLAMA_HOST=http://localhost:11434

# Default model
MODEL_NAME=qwen3.5:4b

# Backend FastAPI server port
PORT=8000

# Frontend Vite dev server port
FRONTEND_PORT=5173

# Frontend API URL (leave blank to use relative proxy /api)
VITE_API_URL=http://localhost:8000
```

> **Security Note:** Sensitive keys or passwords must never be added to `.env`. All `.env` files (except `.env.example`) are ignored by `.gitignore`.

---

## 💻 Running the Application

### Quick Start (Single Command — All Platforms)

To launch the full stack (Ollama check, FastAPI backend with auto-reload, and Vite frontend dev server):

- **Linux & macOS**:
  ```bash
  .venv/bin/python main.py
  ```
- **Windows (PowerShell or CMD)**:
  ```powershell
  .\.venv\Scripts\python.exe main.py
  ```
  *(Or if your virtual environment is already activated, simply: `python main.py`)*

Once launched, access the application in your browser:
- 🖥️ **Kiosk Frontend**: [http://localhost:5173](http://localhost:5173)
- ⚙️ **Backend API**: [http://localhost:8000](http://localhost:8000)
- 📖 **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 🖼️ **Static Festival Posters**: `http://localhost:8000/posters/<poster-filename>`

To stop all services simultaneously, press `Ctrl+C` in the terminal.

---

## ⛶ Fullscreen Kiosk Mode

The Drishti 2026 AI Assistant is designed to run exclusively in **Full Screen Mode** on kiosk hardware:
1. **Automatic Fullscreen Prompt**: When the application is opened, if the browser is not in fullscreen mode, a full-screen blocker is displayed.
2. **One-Touch Activation**: Clicking anywhere on the screen or clicking **"Ask a Question"** instantly launches the browser into full screen.
3. **Exit Protection**: If the browser leaves full screen for any reason, the application safely pauses and displays the full screen prompt until full screen is restored, ensuring an uninterrupted festival showcase.

---

### Running Services Separately (Optional)

If running across different machines or in containerized setups, components can be started individually:

#### Terminal 1 — Ollama:
```bash
ollama serve
```

#### Terminal 2 — FastAPI Backend:
- **Linux/macOS**: `.venv/bin/python -m uvicorn src.server:app --host 0.0.0.0 --port 8000 --reload`
- **Windows**: `.\.venv\Scripts\python.exe -m uvicorn src.server:app --host 0.0.0.0 --port 8000 --reload`

#### Terminal 3 — Vite Frontend:
```bash
cd ui
npm run dev -- --host --port 5173
```

---

## 🛠️ Performance & Tuning Tips

- **CPU Thread Optimization**: The backend auto-allocates optimal thread budgets (`num_thread: 10` for 6-core/12-thread processors). If deploying on different hardware, you can adjust `num_thread` in `src/rag_engine.py` to match physical CPU core counts.
- **Thinking Tokens**: Qwen 3.5 has thinking capabilities disabled (`"think": False`) in the RAG pipeline. This saves 50–90 seconds of unnecessary latency per query.
- **RAM Warmup**: FastAPI pre-warms the model in memory on startup with `"keep_alive": -1` to prevent cold-start disk reads.

---

## 🤝 Contributing

Built with ❤️ by the **NeuraCET** team for Drishti 2026. If you are developing new features, creating tests, or updating festival documentation, please branch off `rag-pipeline` and submit a Pull Request.
