import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.chatbot import chat
from dotenv import load_dotenv

load_dotenv()

# ── App Setup ───────────────────────────────────────────
app = FastAPI(
    title       = "ShopMind AI API",
    description = "Intelligent Shopping Assistant powered by Groq + RAG",
    version     = "1.0.0"
)

# ── CORS (allows React frontend to talk to this API) ────
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ── In-memory session storage ───────────────────────────
sessions: dict = {}

# ── Request/Response Models ─────────────────────────────
class ChatRequest(BaseModel):
    message    : str
    session_id : str = "default"

class ProductInfo(BaseModel):
    name          : str
    main_category : str
    sub_category  : str
    discount_price: str
    actual_price  : str
    ratings       : str
    no_of_ratings : str
    discount_pct  : int
    image         : str
    link          : str

class ChatResponse(BaseModel):
    reply    : str
    products : list
    session_id: str


# ── Routes ──────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "status" : "✅ ShopMind AI is running!",
        "version": "1.0.0",
        "docs"   : "/docs"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint.
    Send a message, get AI response + product recommendations.
    """
    # Get or create session history
    if request.session_id not in sessions:
        sessions[request.session_id] = []

    history = sessions[request.session_id]

    # Get AI response
    reply, updated_history, products = chat(
        request.message,
        history
    )

    # Save updated history
    sessions[request.session_id] = updated_history

    # Keep only last 10 messages (memory management)
    if len(sessions[request.session_id]) > 10:
        sessions[request.session_id] = sessions[request.session_id][-10:]

    return ChatResponse(
        reply      = reply,
        products   = products,
        session_id = request.session_id
    )


@app.delete("/session/{session_id}")
def clear_session(session_id: str):
    """Clear conversation history for a session."""
    if session_id in sessions:
        del sessions[session_id]
    return {"message": f"Session {session_id} cleared"}


@app.get("/categories")
def get_categories():
    """Return available product categories."""
    return {
        "categories": [
            "electronics",
            "fashion",
            "sports & fitness",
            "home & kitchen",
            "accessories",
            "appliances",
            "beauty",
            "kids fashion"
        ]
    }