"""FastAPI Backend Server for Drishti 2026 Assistant.

Provides:
- POST /api/ask: RAG query endpoint returning answer, source, and 2026 poster
- GET /api/health: Health check endpoint
- Static file serving at /posters: Serves festival posters
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.poster_registry import POSTERS_DIR
from src.rag_engine import engine

ROOT_DIR = Path(__file__).resolve().parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up / initialize RAG engine on startup
    print("[Server] Initializing RAG Knowledge Engine...", flush=True)
    engine.initialize()
    print("[Server] RAG Engine ready to serve queries.", flush=True)

    # Pre-warm Ollama model in background thread to avoid delaying server readiness
    def _warmup():
        try:
            import requests
            from src.rag_engine import MODEL_NAME, OLLAMA_URL
            print(f"[Server] Warming up Ollama model '{MODEL_NAME}' in memory...", flush=True)
            requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": MODEL_NAME,
                    "messages": [{"role": "user", "content": "ping"}],
                    "stream": False,
                    "think": False,
                    "keep_alive": -1,
                    "options": {"num_predict": 1},
                },
                timeout=20,
            )
            print("[Server] Ollama model warmed up and resident in RAM.", flush=True)
        except Exception as e:
            print(f"[Server] Note: Ollama pre-warm skipped ({e})", flush=True)

    import threading
    threading.Thread(target=_warmup, daemon=True).start()

    yield


app = FastAPI(
    title="Drishti 2026 AI Assistant API",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for local Vite development and kiosk access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static posters directory
if POSTERS_DIR.exists():
    app.mount("/posters", StaticFiles(directory=str(POSTERS_DIR)), name="posters")


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    source: str
    poster: Optional[str] = None


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "service": "Drishti 2026 Assistant",
        "knowledge_chunks": len(engine.chunks) if engine.initialized else 0,
    }


@app.post("/api/ask", response_model=AskResponse)
async def ask_question(req: AskRequest):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        result = engine.ask(question)
        return AskResponse(
            answer=result["answer"],
            source=result.get("source", "Official Drishti Knowledge Base"),
            poster=result.get("poster"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")


@app.post("/api/ask-stream")
async def ask_question_stream(req: AskRequest):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    return StreamingResponse(
        engine.stream_ask(question),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("src.server:app", host="0.0.0.0", port=port, reload=False)
