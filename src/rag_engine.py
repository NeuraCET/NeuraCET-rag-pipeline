"""RAG Engine for Drishti 2026 Assistant.

Combines BM25 and Dense SentenceTransformer embeddings for hybrid retrieval,
enforces anti-hallucination constraints, cheerful tone, and queries Ollama (qwen3.5:4b).
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

import numpy as np
import requests

from src.ingest import DocumentChunk, load_all_chunks
from src.poster_registry import registry

CACHE_DIR = Path(__file__).resolve().parent.parent / ".rag_cache"
OLLAMA_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = "qwen3.5:4b"

SYSTEM_PROMPT = """You are the friendly, cheerful, and enthusiastic AI guide for Drishti Fest at the College of Engineering Trivandrum (CET)!
Your tone is always bright, warm, cheerful, happy, and genuinely informative!

CRITICAL INSTRUCTIONS & ANTI-HALLUCINATION POLICY:
1. You only have knowledge about Drishti Fest events based on the provided Context.
2. If the user asks ANY question about topics, trivia, or events not present in the Context (or general world knowledge outside of Drishti), DO NOT ANSWER IT using external knowledge.
3. If no information is found in the Context, respond cheerfully and warmly with:
"Hello! 😊 I'd love to help, but there is no information available about that in the official Drishti records! Feel free to ask me about any of our exciting Drishti 2026 events, workshops, competitions, or AI Summit talks!"
4. For events from past editions (e.g. Drishti 2024 or 2022), happily share the facts found in the Context and mention cheerfully that they occurred during previous editions of Drishti.
5. Provide complete, accurate details (Event Name, Dates, Venue, Fees, Requirements, Coordinators with phone numbers) in clean Markdown bullet points. Be direct, cheerful, and crisp without filler padding, and ensure all information is fully stated.
"""


def simple_tokenize(text: str) -> List[str]:
    """Basic word tokenizer for BM25."""
    return re.findall(r"\w+", text.lower())


class RAGEngine:
    def __init__(self):
        self.chunks: List[DocumentChunk] = []
        self.bm25 = None
        self.embed_model = None
        self.chunk_embeddings: Optional[np.ndarray] = None
        self.initialized = False

    def initialize(self, force_recompute: bool = False):
        """Index all documents from dataRAG/."""
        if self.initialized and not force_recompute:
            return

        print("[RAG] Ingesting documents from dataRAG/...", flush=True)
        self.chunks = load_all_chunks()
        print(f"[RAG] Ingested {len(self.chunks)} knowledge chunks.", flush=True)

        # 1. Initialize BM25
        try:
            from rank_bm25 import BM25Okapi
            corpus_tokens = [simple_tokenize(c.text) for c in self.chunks]
            self.bm25 = BM25Okapi(corpus_tokens)
            print("[RAG] BM25 keyword index ready.", flush=True)
        except Exception as e:
            print(f"[RAG] Warning: BM25 error: {e}", flush=True)

        # 2. Initialize Embeddings (with disk cache)
        self._init_embeddings(force_recompute=force_recompute)
        self.initialized = True

    def _init_embeddings(self, force_recompute: bool = False):
        """Load or compute dense embeddings using sentence-transformers."""
        CACHE_DIR.mkdir(exist_ok=True)
        cache_file = CACHE_DIR / "embeddings.npy"

        try:
            from sentence_transformers import SentenceTransformer
            print("[RAG] Loading embedding model 'all-MiniLM-L6-v2'...", flush=True)
            self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")

            if not force_recompute and cache_file.exists():
                try:
                    loaded = np.load(cache_file)
                    if len(loaded) == len(self.chunks):
                        self.chunk_embeddings = loaded
                        print("[RAG] Loaded cached dense embeddings.", flush=True)
                        return
                except Exception:
                    pass

            # Compute and cache embeddings
            texts = [c.text for c in self.chunks]
            embeddings = self.embed_model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            self.chunk_embeddings = embeddings
            np.save(cache_file, embeddings)
            print("[RAG] Dense embeddings computed and cached.", flush=True)
        except Exception as e:
            print(f"[RAG] Note: Dense embeddings unavailable ({e}), using keyword retrieval.", flush=True)

    def retrieve(self, query: str, top_k: int = 3) -> Tuple[List[Tuple[DocumentChunk, float]], float, float]:
        """Hybrid retrieval combining BM25 keyword ranking and dense semantic similarity."""
        if not self.chunks:
            return [], 0.0, 0.0

        n_chunks = len(self.chunks)
        bm25_scores = np.zeros(n_chunks)
        raw_max_bm = 0.0
        raw_max_dense = 0.0

        # BM25 scoring
        if self.bm25:
            tokens = simple_tokenize(query)
            if tokens:
                raw_bm25 = np.array(self.bm25.get_scores(tokens))
                raw_max_bm = float(np.max(raw_bm25)) if len(raw_bm25) > 0 else 0.0
                if raw_max_bm > 0:
                    bm25_scores = raw_bm25 / raw_max_bm

        # Dense similarity scoring
        dense_scores = np.zeros(n_chunks)
        if self.embed_model and self.chunk_embeddings is not None:
            try:
                q_vec = self.embed_model.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]
                dot_products = np.dot(self.chunk_embeddings, q_vec)
                raw_max_dense = float(np.max(dot_products)) if len(dot_products) > 0 else 0.0
                dense_scores = np.clip((dot_products + 1) / 2.0, 0, 1)
            except Exception:
                pass

        # Hybrid weighting (0.65 BM25 + 0.35 Dense)
        if raw_max_bm > 0:
            final_scores = 0.65 * bm25_scores + 0.35 * dense_scores
        else:
            final_scores = dense_scores

        top_indices = np.argsort(final_scores)[::-1][:top_k]
        results = [(self.chunks[idx], float(final_scores[idx])) for idx in top_indices]
        return results, raw_max_bm, raw_max_dense

    def ask(self, question: str) -> Dict[str, Any]:
        """Execute full RAG pipeline for a question."""
        self.initialize()

        # 1. Resolve 2026 poster directly from user query
        poster_url = registry.get_poster_for_query(question)

        # 2. Retrieve relevant chunks (maintaining full context)
        top_results, raw_max_bm, raw_max_dense = self.retrieve(question, top_k=3)

        # Strict out-of-domain detection: if no keyword match AND semantic similarity < 0.35
        if raw_max_bm == 0.0 and raw_max_dense < 0.35:
            return {
                "answer": "Hello! 😊 I'd love to help, but there is no information available about that in the official Drishti records! Feel free to ask me about any of our exciting Drishti 2026 events, workshops, competitions, or AI Summit talks!",
                "source": "Official Drishti Knowledge Base",
                "poster": None,
            }

        # Format context for prompt - PRESERVING FULL CONTEXT AS REQUESTED
        context_texts = []
        for i, (chunk, score) in enumerate(top_results):
            source = chunk.metadata.get("source", "Drishti Data")
            edition = chunk.metadata.get("edition", "2026")
            context_texts.append(f"--- Document {i+1} [{source} | Edition {edition}] ---\n{chunk.text}")
        
        full_context = "\n\n".join(context_texts)

        # 3. Generate response via Ollama with think: False and no token cutoff
        try:
            payload = {
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Context:\n{full_context}\n\nQuestion: {question}\n\nProvide a cheerful, happy, and complete answer based STRICTLY on the Context above. If not in the context, say no information is available:",
                    },
                ],
                "stream": False,
                "think": False,
                "keep_alive": -1,
                "options": {
                    "temperature": 0.2,
                    "top_p": 0.9,
                    "num_ctx": 2048,
                    "num_predict": 800,  # Generous budget so answers are never truncated
                    "num_thread": 10,    # 10 threads benchmarked fastest on 6-core/12-thread Ryzen CPU
                },
            }

            resp = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=180)
            if resp.status_code == 200:
                answer = resp.json().get("message", {}).get("content", "").strip()
            else:
                answer = f"I'm eager to help you explore Drishti! However, I had a brief hiccup connecting to my language model ({resp.status_code}). Please try again!"
        except Exception as e:
            answer = f"I'm excited for Drishti 2026, but I ran into an error generating the answer: {e}"

        return {
            "answer": answer,
            "source": "Official Drishti Knowledge Base",
            "poster": poster_url,
        }

    def stream_ask(self, question: str) -> Iterator[str]:
        """Execute full RAG pipeline and yield streaming SSE/JSON events."""
        self.initialize()

        # 1. Resolve 2026 poster directly from user query
        poster_url = registry.get_poster_for_query(question)

        # 2. Retrieve relevant chunks (maintaining full context)
        top_results, raw_max_bm, raw_max_dense = self.retrieve(question, top_k=3)

        # Emit initial metadata event
        yield json.dumps({
            "type": "meta",
            "poster": poster_url,
            "source": "Official Drishti Knowledge Base",
        }) + "\n"

        # Strict out-of-domain detection: if no keyword match AND semantic similarity < 0.35
        if raw_max_bm == 0.0 and raw_max_dense < 0.35:
            msg = (
                "Hello! 😊 I'd love to help, but there is no information available about that "
                "in the official Drishti records! Feel free to ask me about any of our exciting "
                "Drishti 2026 events, workshops, competitions, or AI Summit talks!"
            )
            yield json.dumps({"type": "token", "content": msg}) + "\n"
            yield json.dumps({"type": "done"}) + "\n"
            return

        # Format context for prompt - PRESERVING FULL CONTEXT AS REQUESTED
        context_texts = []
        for i, (chunk, score) in enumerate(top_results):
            source = chunk.metadata.get("source", "Drishti Data")
            edition = chunk.metadata.get("edition", "2026")
            context_texts.append(f"--- Document {i+1} [{source} | Edition {edition}] ---\n{chunk.text}")

        full_context = "\n\n".join(context_texts)

        # 3. Stream response via Ollama
        try:
            payload = {
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Context:\n{full_context}\n\nQuestion: {question}\n\nProvide a cheerful, happy, and complete answer based STRICTLY on the Context above. If not in the context, say no information is available:",
                    },
                ],
                "stream": True,
                "think": False,
                "keep_alive": -1,
                "options": {
                    "temperature": 0.2,
                    "top_p": 0.9,
                    "num_ctx": 2048,
                    "num_predict": 800,
                    "num_thread": 10,
                },
            }

            resp = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, stream=True, timeout=(10, 180))
            for line in resp.iter_lines():
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        yield json.dumps({"type": "token", "content": token}) + "\n"
                    if chunk.get("done"):
                        yield json.dumps({"type": "done"}) + "\n"
                        return
        except Exception as e:
            err_msg = f"I'm excited for Drishti 2026, but I ran into an error generating the answer: {e}"
            yield json.dumps({"type": "token", "content": err_msg}) + "\n"
            yield json.dumps({"type": "done"}) + "\n"


# Global singleton
engine = RAGEngine()
