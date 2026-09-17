# Drishti 2026 AI Kiosk Assistant — NeuraCET

[![Event](https://img.shields.io/badge/Event-Drishti%202026-gold.svg)](https://drishti.cet.ac.in)
[![Maintained by](https://img.shields.io/badge/Maintained%20by-NeuraCET-blue.svg)](#)
[![Model](https://img.shields.io/badge/LLM-Qwen%203.5%20(4B)-green.svg)](https://ollama.com/library/qwen3.5:4b)
[![Retrieval](https://img.shields.io/badge/Retrieval-Hybrid%20(BM25%20%2B%20Dense)-purple.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](#)

An intelligent, interactive, and offline-capable RAG (Retrieval-Augmented Generation) assistant built for the **Drishti 2026** tech fest at the **College of Engineering Trivandrum (CET)**. Running as an interactive kiosk, it provides real-time event schedules, workshop details, rules, coordinator contacts, and official 2026 festival posters with **zero hallucinations** and a cheerful, welcoming personality.

---

## 🌟 Key Highlights

- **Automatic Kiosk Fullscreen & Lock**: Clicking **"Ask a Question"** automatically engages fullscreen kiosk mode and activates keyboard locks to prevent accidental exits. Fullscreen can only be unlocked with the organizer shortcut **`Ctrl + Shift + F`**.
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

- **Python 3.10+** (Python 3.11 or 3.12 recommended)
- **Node.js 18+** & **npm**
- **Ollama**: Download and install from [ollama.com](https://ollama.com)
- **`poppler-utils`** (recommended for clean PDF text extraction via `pdftotext`):
  - **Debian / Ubuntu / Mint**:
    ```bash
    sudo apt update && sudo apt install -y poppler-utils
    ```
  - **macOS (Homebrew)**:
    ```bash
    brew install poppler
    ```
  - **Arch Linux**:
    ```bash
    sudo pacman -S poppler
    ```
  - **Windows (WSL2)**:
    ```bash
    sudo apt update && sudo apt install -y poppler-utils
    ```

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

# Pull the model (in another terminal)
ollama pull qwen3.5:4b
```

---

### 4. Python Environment Setup

You can use [`uv`](https://github.com/astral-sh/uv) (recommended for fast installs) or standard `venv`:

#### Using `uv` (Recommended):
```bash
# Create virtual environment
uv venv

# Install all backend dependencies
uv pip install -e .
```

#### Using Standard `python3 -m venv`:
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

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

```bash
cp .env.example .env
```

The default values are configured for local execution and require no changes under normal circumstances:

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

### Quick Start (Single Command)

To launch the full stack (Ollama status check, FastAPI backend with auto-reload, and Vite frontend dev server):

```bash
# Run with the virtual environment's python
.venv/bin/python main.py
```

Once launched, access the application in your browser:
- 🖥️ **Kiosk Frontend**: [http://localhost:5173](http://localhost:5173)
- ⚙️ **Backend API**: [http://localhost:8000](http://localhost:8000)
- 📖 **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 🖼️ **Static Festival Posters**: `http://localhost:8000/posters/<poster-filename>`

To stop all services simultaneously, press `Ctrl+C` in the terminal.

---

### Running Services Separately (Optional)

If running across different machines or in containerized setups, components can be started individually:

#### Terminal 1 — Ollama:
```bash
ollama serve
```

#### Terminal 2 — FastAPI Backend:
```bash
.venv/bin/python -m uvicorn src.server:app --host 0.0.0.0 --port 8000 --reload
```

#### Terminal 3 — Vite Frontend:
```bash
cd ui
npm run dev -- --host --port 5173
```

---

## 🔒 Kiosk Fullscreen Mode & Organizer Controls

To provide a seamless and secure unattended kiosk experience during Drishti 2026:

1. **Automatic Fullscreen Launch**:
   - When a visitor clicks **"Ask a Question"** on the welcome screen, the web application automatically requests browser fullscreen mode.
2. **Kiosk Escape Prevention**:
   - The Chromium Keyboard Lock API (`navigator.keyboard.lock(['Escape'])`) is activated to suppress accidental exits via the `Escape` key.
   - Pressing `Escape` is captured and blocked by the kiosk state machine while locked.
   - If fullscreen is ever exited through system shortcuts or external dialogs, an automatic **Kiosk Fullscreen Locked** recovery overlay prompts the operator or visitor to tap anywhere on the screen to immediately re-enter fullscreen.
3. **Organizer Unlock Shortcut**:
   - To unlock kiosk mode and exit full screen, press:
     ```text
     Ctrl + Shift + F   (or Cmd + Shift + F on macOS)
     ```
   - This immediately unlocks the keyboard, exits fullscreen mode, and displays a temporary status notification.

---

## 🛠️ Performance & Tuning Tips

- **CPU Thread Optimization**: The backend auto-allocates optimal thread budgets (`num_thread: 10` for 6-core/12-thread processors). If deploying on different hardware, you can adjust `num_thread` in `src/rag_engine.py` to match physical CPU core counts.
- **Thinking Tokens**: Qwen 3.5 has thinking capabilities disabled (`"think": False`) in the RAG pipeline. This saves 50–90 seconds of unnecessary latency per query.
- **RAM Warmup**: FastAPI pre-warms the model in memory on startup with `"keep_alive": -1` to prevent cold-start disk reads.

---

## 🤝 Contributing

Built with ❤️ by the **NeuraCET** team for Drishti 2026. If you are developing new features, creating tests, or updating festival documentation, please branch off `rag-pipeline` and submit a Pull Request.
