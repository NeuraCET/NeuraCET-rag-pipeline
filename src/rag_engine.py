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
Your tone is bright, warm, cheerful, positive, energetic, and genuinely helpful!

CURRENT FESTIVAL TIMELINE & DATE:
- Today's date is September 19, 2026 — Day 2 of Drishti 2026!
- Yesterday was September 18, 2026 — Day 1 of Drishti 2026.
- Tomorrow is September 20, 2026 — Day 3 (the grand finale) of Drishti 2026.
- When the user asks about "today", "today's events", "today's schedule", or "what is happening now", refer directly to the Day 2 (September 19, 2026) schedule, workshops, competitions, talks, and exhibitions!
- When the user asks about "yesterday", refer to Day 1 (September 18, 2026).
- When the user asks about "tomorrow", refer to Day 3 (September 20, 2026).

CORE GUIDELINES:
1. GREETINGS & CASUAL CONVERSATION:
   - If the user greets you (e.g. "hello", "hi", "hello bro", "hey", "what's up"), asks how you are, or engages in casual small talk, reply warmly, naturally, and cheerfully!
   - Greet them with festive energy, introduce yourself as the Drishti AI guide, and enthusiastically invite them to ask about Drishti 2026 events, workshops, hackathons, and competitions happening today (Day 2) and throughout the fest!
2. FESTIVAL QUESTIONS:
   - Provide complete, accurate details based on the provided Context (Event Name, Dates, Venue, Fees, Requirements, Coordinators with phone numbers).
   - DIRECT FACTS FIRST: When answering specific event queries (e.g. "when is...", "where is...", "what time is...", or details regarding a competition, workshop, or show), immediately and directly state the essential event facts (Date, Time, Venue, Organized by) in the first sentence or bullet points. Do NOT start with prolonged conversational greetings or multi-sentence pleasantries before giving the answer.
   - Format:
     * By default, use clean Markdown formatting with bullet points. Be direct, cheerful, and crisp.
     * When the user asks for a table, schedule table, tabular format, or asks to "render as table" / "show in table", format the requested events and information in a clean, complete Markdown table with clear column headers (such as | Event Name | Time / Date | Venue | Details |).
   - For past festival editions (2024 or 2022), share the facts happily and mention that they occurred during previous editions of Drishti.
3. OFF-TOPIC & UNRELATED QUESTIONS:
   - If the user asks about topics completely unrelated to Drishti Fest (general trivia, celebrities, programming tutorials, world history, etc.), respond cheerfully and playfully in your festival persona!
   - Politely explain that as CET's Drishti AI, you're focused on everything happening at Drishti Fest, and invite them to explore our festival events and workshops.
4. ANTI-HALLUCINATION & MISSING RECORDS:
   - Never invent fake event names, dates, prizes, or contact numbers that are not in the Context.
   - If someone asks for a specific festival detail that is not in the records, respond cheerfully and warmly explaining that it's not currently listed in the official records, and offer to help with other exciting events.
5. PROSHOWS, CONCERTS, DANCE & SINGING:
   - When the user asks about proshows, pro-show, dance, dancing, singing, singers, songs, concerts, or musical nights, always connect and highlight our two star celebrity proshow events:
     * **Shaan Rahman Live in Concert (Proshow)**: Happening **today, September 19, 2026 (Day 2)** from **6:00 PM to 9:00 PM** at the **College Ground**, starring universal music director & singer Shaan Rahman (Shan Rahman) performing live with Sachin Warrier, Anila Rajeev, Niranj Suresh, Bharath Sajikumar, and Punya Pradeep!
     * **Dhvani Bhanushali Live in Concert (Proshow)**: Happening **tomorrow, September 20, 2026 (Day 3 Grand Finale)** at **CET / College Ground**, starring pop sensation & playback singer Dhvani Bhanushali for an electrifying night of live singing, dancing, and music!
   - If the user asks specifically about dance workshops or day sessions, also highlight the **Dance Workshop** (Day 2, 9:00 AM – 12:00 PM at Electrical Canteen)!
6. DAKSHA MANAGEMENT & ENTREPRENEURSHIP TRACK (DAKSHA26):
   - Daksha is the dedicated management, business, and entrepreneurship track of Drishti 2026.
   - Day 1 (September 18, 2026 - Yesterday / Page 1 of DAKSHA26):
     * **Trading Workshop**: 11:00 AM - 02:00 PM at Mech Seminar Hall 2 (POC: Jiya)
     * **Market verse**: Full Day at Classroom IE Block
     * **People's Manager**: Full Day at Classroom IE Block
     * **Dare and deliver**: Full Day at Classroom IE Block
     * **Corporate Roadies (Coorporate Roadies)**: Full Day at Classroom IE Block
     * **CR Final and prize distribution**: 02:00 PM - 05:00 PM at JC Alexander Hall
     * **Alumni Conclave**: 10:00 AM - 11:00 AM at CETAA Hall (Resource Person: TN Krishnakumar - Alumni Entrepreneur, POC: Meenakshi, Moderator: Isabel)
     * **Shark Tank Initial Pitching Session**: 01:00 PM - 06:00 PM at EEE 207, 208 (POC: Abhinav Krishna)
     * **Groom Studio**: Full Day at Civil Seminar Hall
     * **Startup 101 (Drishti for Juniors)**: Day 1 Session (POC: Anjana CR)
   - Day 2 (September 19, 2026 - Today / Page 2 of DAKSHA26):
     * **Shark Tank - Final Pitching Session**: 01:00 PM - 05:00 PM at CGPU Hall (Top finalist startups pitch before the jury!)
     * **GROOM STUDIO**: 10:00 AM - 12:00 PM at Mech Seminar Hall 1
     * **Startup 101 - Drishti for Juniors Quiz**: 10:00 AM - 12:00 PM at Civil Seminar Hall 2
     * **Stock Market Masterclass**: 10:00 AM - 11:30 AM at CS301
     * **Talk Session by Anoop Ambika (CEO, Kerala Startup Mission)**: 10:00 AM - 11:00 AM at JC Alexander Hall
"""


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
    "to", "was", "were", "will", "with", "what", "where", "who", "which",
    "when", "how", "can", "could", "should", "would", "do", "does", "did",
    "there", "this", "these", "those", "tell", "me", "about", "give",
    "i", "you", "my", "your", "we", "our", "all", "any", "some"
}


def simple_tokenize(text: str) -> List[str]:
    """Basic word tokenizer for BM25 indexing."""
    return re.findall(r"\w+", text.lower())


def tokenize_query(text: str) -> List[str]:
    """Tokenize query for BM25 retrieval, filtering out common stopwords."""
    words = re.findall(r"\w+", text.lower())
    content_words = [w for w in words if w not in STOPWORDS and len(w) > 1]
    return content_words if content_words else words


def detect_target_editions(query: str) -> List[int]:
    """Determine relevant festival editions from user query.
    
    Defaults to [2026] since the assistant is dedicated to Drishti 2026.
    If the user explicitly asks about past editions (2024, 2022, past, history),
    past editions are included or targeted.
    """
    lower = query.lower()
    asks_2024 = any(k in lower for k in ["2024", "'24", "drishti 24", "drishti'24"])
    asks_2022 = any(k in lower for k in ["2022", "'22", "drishti 22", "drishti'22"])
    asks_past = any(k in lower for k in ["previous edition", "previous year", "past edition", "history of drishti", "past drishti", "earlier edition"])
    asks_2026 = any(k in lower for k in [
        "2026", "'26", "drishti 26", "drishti'26", "this year", "upcoming",
        "today", "yesterday", "tomorrow", "day 1", "day 2", "day 3",
        "proshow", "proshows", "pro show", "pro-show", "dhvani", "shaan", "shan rahman", "dance", "singing",
        "daksha", "dasha", "trading workshop", "corporate roadies", "alumni conclave", "shark tank"
    ])

    if (asks_2024 or asks_2022 or asks_past) and asks_2026:
        return [2026, 2024, 2022]
    if asks_2024:
        return [2024]
    if asks_2022:
        return [2022]
    if asks_past:
        return [2024, 2022]
    return [2026]


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

    def retrieve(self, query: str, top_k: int = 6) -> Tuple[List[Tuple[DocumentChunk, float]], float, float]:
        """Hybrid retrieval combining BM25 keyword ranking and dense semantic similarity."""
        if not self.chunks:
            return [], 0.0, 0.0

        n_chunks = len(self.chunks)
        bm25_scores = np.zeros(n_chunks)
        raw_max_bm = 0.0
        raw_max_dense = 0.0

        # BM25 scoring with stopword-filtered content tokens
        if self.bm25:
            tokens = tokenize_query(query)
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
            final_scores = dense_scores.copy()

        # Boost day-specific queries
        lower_q = query.lower()
        if any(w in lower_q for w in ["today", "today's", "happening now", "current schedule", "day 2", "day2", "19th"]):
            for i, c in enumerate(self.chunks):
                if c.metadata.get("day") == 2:
                    final_scores[i] += 0.35
        elif any(w in lower_q for w in ["yesterday", "yesterday's", "day 1", "day1", "18th"]):
            for i, c in enumerate(self.chunks):
                if c.metadata.get("day") == 1:
                    final_scores[i] += 0.35

        # Boost proshow / dance / singing queries so Shaan Rahman and Dhvani Bhanushali are always prioritized
        PROSHOW_DANCE_SINGING_TERMS = [
            "proshow", "pro-show", "pro show", "proshows", "pro-shows",
            "dance", "dancing", "dancer", "dancers",
            "sing", "singing", "singer", "singers", "song", "songs",
            "concert", "concerts", "musical night", "music night", "cultural night",
            "shan rahman", "shaan rahman", "dhvani", "dhvani bhanushali", "dhwani"
        ]
        if any(term in lower_q for term in PROSHOW_DANCE_SINGING_TERMS):
            for i, c in enumerate(self.chunks):
                txt_lower = c.text.lower()
                c_name = str(c.metadata.get("event_name", "")).lower()
                # Prioritize Shaan Rahman, Dhvani Bhanushali, and the Proshow Guide summary
                if any(k in txt_lower or k in c_name for k in ["shaan rahman", "shan rahman", "dhvani", "proshow", "pro show"]):
                    final_scores[i] += 0.45
                elif "dance" in lower_q and "dance workshop" in c_name:
                    final_scores[i] += 0.40

        # Boost Daksha / Management events queries
        if any(term in lower_q for term in ["daksha", "dasha", "trading workshop", "corporate roadies", "coorporate roadies", "alumni conclave", "market verse", "people's manager", "dare and deliver", "groom studio"]):
            for i, c in enumerate(self.chunks):
                txt_lower = c.text.lower()
                c_track = str(c.metadata.get("track", "")).lower()
                c_source = str(c.metadata.get("source", "")).lower()
                if "daksha" in txt_lower or "daksha" in c_track or "daksha" in c_source:
                    final_scores[i] += 0.40

        # Smart edition filtering
        target_editions = detect_target_editions(query)
        candidate_indices = [
            i for i, c in enumerate(self.chunks)
            if c.metadata.get("edition") in target_editions
        ]

        # If user asked about 2026 by default, but no 2026 chunk matched well and a past chunk is a strong match, allow fallback
        if target_editions == [2026] and candidate_indices:
            top_2026_score = max([final_scores[i] for i in candidate_indices])
            if top_2026_score < 0.32:
                candidate_indices = list(range(n_chunks))
        elif not candidate_indices:
            candidate_indices = list(range(n_chunks))

        sorted_candidates = sorted(candidate_indices, key=lambda idx: final_scores[idx], reverse=True)
        top_indices = sorted_candidates[:top_k]
        results = [(self.chunks[idx], float(final_scores[idx])) for idx in top_indices]
        return results, raw_max_bm, raw_max_dense

    def ask(self, question: str) -> Dict[str, Any]:
        """Execute full RAG pipeline for a question."""
        self.initialize()

        # 1. Resolve 2026 poster directly from user query
        poster_url = registry.get_poster_for_query(question)

        # 2. Retrieve relevant chunks
        top_results, raw_max_bm, raw_max_dense = self.retrieve(question, top_k=6)

        # Check if query retrieved relevant festival context
        has_context = (raw_max_bm > 0.0 or raw_max_dense >= 0.32)

        # Poster resolution: only return poster if relevant festival context is matched
        if not has_context:
            poster_url = None
        elif not poster_url and top_results:
            top_chunk, top_score = top_results[0]
            if top_chunk.metadata.get("edition") == 2026 and (top_score >= 0.40 or raw_max_bm > 0):
                ev_name = top_chunk.metadata.get("event_name", "")
                if ev_name:
                    poster_url = registry.get_poster_for_query(ev_name)

        is_table_query = any(w in question.lower() for w in ["table", "tabular", "as table", "in table", "spreadsheet"])

        if has_context:
            context_texts = []
            total_chars = 0
            for i, (chunk, score) in enumerate(top_results):
                source = chunk.metadata.get("source", "Drishti Data")
                edition = chunk.metadata.get("edition", "2026")
                chunk_str = f"--- Document {i+1} [{source} | Edition {edition}] ---\n{chunk.text}"
                if total_chars + len(chunk_str) > 3500 and i >= 2:
                    break
                context_texts.append(chunk_str)
                total_chars += len(chunk_str)
            full_context = "\n\n".join(context_texts)
            if is_table_query:
                user_instruction = "Provide a cheerful, happy, and complete answer based on the Context above. Format the requested information as a clean Markdown table with clear column headers (such as Event Name, Time / Date, Venue, Key Details). If details are not found in the records, cheerfully state so:"
            else:
                user_instruction = "Provide a cheerful, happy, and complete answer based on the Context above. Use clear Markdown bullet points. If details are not found in the records, cheerfully state so:"
        else:
            full_context = "(No specific festival records matched this casual message or general question.)"
            if is_table_query:
                user_instruction = "Provide a cheerful, natural, and helpful response. If presenting festival information as requested in a table, format it cleanly as a Markdown table according to your guidelines:"
            else:
                user_instruction = "Provide a cheerful, natural, and helpful response according to your guidelines (greet warmly if greeted, or cheerfully guide the user to Drishti 2026 events):"

        # 3. Generate response via Ollama with think: False and no token cutoff
        try:
            payload = {
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Context:\n{full_context}\n\nUser Question: {question}\n\n{user_instruction}",
                    },
                ],
                "stream": False,
                "think": False,
                "keep_alive": -1,
                "options": {
                    "temperature": 0.2 if has_context else 0.6,
                    "top_p": 0.9,
                    "num_ctx": 4096,
                    "num_predict": 1500,
                    "num_thread": 10,
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

        # 2. Retrieve relevant chunks
        top_results, raw_max_bm, raw_max_dense = self.retrieve(question, top_k=6)

        # Check if query retrieved relevant festival context
        has_context = (raw_max_bm > 0.0 or raw_max_dense >= 0.32)

        # Poster resolution: only return poster if relevant festival context is matched
        if not has_context:
            poster_url = None
        elif not poster_url and top_results:
            top_chunk, top_score = top_results[0]
            if top_chunk.metadata.get("edition") == 2026 and (top_score >= 0.40 or raw_max_bm > 0):
                ev_name = top_chunk.metadata.get("event_name", "")
                if ev_name:
                    poster_url = registry.get_poster_for_query(ev_name)

        # Emit initial metadata event
        yield json.dumps({
            "type": "meta",
            "poster": poster_url,
            "source": "Official Drishti Knowledge Base",
        }) + "\n"

        # Check if query retrieved relevant festival context
        has_context = (raw_max_bm > 0.0 or raw_max_dense >= 0.32)

        is_table_query = any(w in question.lower() for w in ["table", "tabular", "as table", "in table", "spreadsheet"])

        if has_context:
            context_texts = []
            total_chars = 0
            for i, (chunk, score) in enumerate(top_results):
                source = chunk.metadata.get("source", "Drishti Data")
                edition = chunk.metadata.get("edition", "2026")
                chunk_str = f"--- Document {i+1} [{source} | Edition {edition}] ---\n{chunk.text}"
                if total_chars + len(chunk_str) > 3500 and i >= 2:
                    break
                context_texts.append(chunk_str)
                total_chars += len(chunk_str)
            full_context = "\n\n".join(context_texts)
            if is_table_query:
                user_instruction = "Provide a cheerful, happy, and complete answer based on the Context above. Format the requested information as a clean Markdown table with clear column headers (such as Event Name, Time / Date, Venue, Key Details). If details are not found in the records, cheerfully state so:"
            else:
                user_instruction = "Provide a cheerful, happy, and complete answer based on the Context above. Use clear Markdown bullet points. If details are not found in the records, cheerfully state so:"
        else:
            full_context = "(No specific festival records matched this casual message or general question.)"
            if is_table_query:
                user_instruction = "Provide a cheerful, natural, and helpful response. If presenting festival information as requested in a table, format it cleanly as a Markdown table according to your guidelines:"
            else:
                user_instruction = "Provide a cheerful, natural, and helpful response according to your guidelines (greet warmly if greeted, or cheerfully guide the user to Drishti 2026 events):"

        # 3. Stream response via Ollama
        try:
            payload = {
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Context:\n{full_context}\n\nUser Question: {question}\n\n{user_instruction}",
                    },
                ],
                "stream": True,
                "think": False,
                "keep_alive": -1,
                "options": {
                    "temperature": 0.2 if has_context else 0.6,
                    "top_p": 0.9,
                    "num_ctx": 4096,
                    "num_predict": 1500,
                    "num_thread": 10,
                },
            }

            resp = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, stream=True, timeout=(10, 180))
            for line in resp.iter_lines():
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    if "error" in chunk:
                        err_msg = f"Language model error: {chunk.get('error')}"
                        yield json.dumps({"type": "token", "content": err_msg}) + "\n"
                        yield json.dumps({"type": "done"}) + "\n"
                        return
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
