from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama

from RAG.rag import RagIndex, run_query 

app = FastAPI()

index = RagIndex()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

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
    
    response = ollama.chat(model='qwen3.5:4b', messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ])
    
    return {
        "answer": response['message']['content'],
        "posters": posters  
    }