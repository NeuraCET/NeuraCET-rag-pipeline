from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import ollama

from RAG.rag import RagIndex, run_query 

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
POSTER_DIR = PROJECT_ROOT / "posters"

app = FastAPI(title="Drishti RAG Assistant API")

if POSTER_DIR.exists():
    app.mount("/posters", StaticFiles(directory=str(POSTER_DIR)), name="posters")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "service": "Drishti RAG Assistant Backend"}

@app.get("/api/health")
def health():
    return {"status": "healthy"}

class QueryRequest(BaseModel):
    question: str

index = RagIndex()

@app.post("/api/ask")
def ask_drishti(request: QueryRequest):
    
    results, posters, context = run_query(index, request.question)
    
    system_prompt = """You are Drishti AI, the official intelligent assistant for the Drishti 2026 festival and AI Summit at CET.
Answer attendee questions clearly and concisely using only the provided context. If the requested information is not in the context, state that it is currently unavailable.

RULES FOR YOUR RESPONSE:
1. STRUCTURE: Always use Markdown. Use bold headings, bullet points, and short paragraphs so it is easy to read on a screen.
2. IMAGES: If the context provides an image URL (like a map, poster, or logo), you MUST include it using Markdown syntax: ![Description](URL).
3. RECOMMENDATIONS: Act like a proactive guide. If you answer a question about an event, suggest 1 or 2 related events, workshops, or venues mentioned in the context to keep them engaged.
4. TONE: Be energetic, welcoming, and intelligent. 
5. ACCURACY: Only use the information provided in the Context. If the answer isn't there, politely apologize and guide them to the main help desk.
"""

    user_prompt = f"Context provided from database:\n{context}\n\nStudent's Question: {request.question}"
    

    if posters:
        user_prompt += f"\n\nRelevant Poster Images to display: {', '.join(posters)}"
    
    response = ollama.chat(
        model='qwen3.5:4b',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        think=False,
    )
    
    return {
        "answer": response['message']['content'],
        "posters": posters  
    }