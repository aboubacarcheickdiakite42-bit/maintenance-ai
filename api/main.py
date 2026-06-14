from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.ai_engine import chat_with_ai

app = FastAPI(title="ChatGPT Maintenance")


# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- HOME ----------------
@app.get("/")
def home():
    return {"message": "ChatGPT Maintenance fonctionne"}


# ---------------- CHAT IA ----------------
@app.get("/chat")
def chat(message: str):

    response = chat_with_ai(message)

    return {
        "response": response
    }