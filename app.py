import os
import io
import uuid
import asyncio
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form, Request, status
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from PIL import Image
from dotenv import load_dotenv
from google import genai

# Load .env
load_dotenv()

if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("No Gemini API key found. Please set GEMINI_API_KEY in your .env file")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
PRIMARY_MODEL = os.getenv("GEMINI_MODEL") or "gemini-3.5-flash-lite"
FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL") or "gemini-3.8-flash"


def generate_content(contents):
    models = [PRIMARY_MODEL]
    if FALLBACK_MODEL != PRIMARY_MODEL:
        models.append(FALLBACK_MODEL)

    for model_index, model in enumerate(models):
        try:
            return client.models.generate_content(model=model, contents=contents)
        except Exception as error:
            is_unavailable = getattr(error, "code", None) == 503 or "503" in str(error)
            if is_unavailable and model_index < len(models) - 1:
                continue
            raise

# FastAPI app initialization
app = FastAPI(title="PocketSmart: AI Budget Planner")

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ Single import from state at the top
from state import recommendation_history

# Import routers
from routers import home, party, jewelry, auth
from auth import get_current_active_user
from models import UserInDB

app.include_router(auth.router)
app.include_router(home.router)
app.include_router(party.router)
app.include_router(jewelry.router)

# ── Startup Event ──────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    print("✅ PocketSmart AI starting up...")
    print("✅ Gemini API key loaded")
    print("✅ All routers registered")
    print("✅ Server ready!")

@app.get("/startup")
async def startup_status():
    return {
        "status": "running",
        "message": "PocketSmart AI is operational",
        "timestamp": datetime.utcnow().isoformat()
    }

# ── Root → Landing Page ────────────────────────────────────
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# ── Login & Register pages ─────────────────────────────────
@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# ── Dashboard & History pages ──────────────────────────────
@app.get("/dashboard")
async def dashboard(request: Request, current_user: UserInDB = Depends(get_current_active_user)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": current_user})

@app.get("/history")
async def history_page(request: Request, current_user: UserInDB = Depends(get_current_active_user)):
    return templates.TemplateResponse("history.html", {"request": request, "user": current_user})

# ── API History (scoped to the logged-in user) ─────────────
@app.get("/api/history")
async def get_history_api(current_user: UserInDB = Depends(get_current_active_user)):
    user_history = recommendation_history[current_user.username]
    return {
        "total": len(user_history),
        "history": user_history
    }

@app.delete("/api/history")
async def clear_history_api(current_user: UserInDB = Depends(get_current_active_user)):
    recommendation_history[current_user.username].clear()
    return {"message": "History cleared successfully"}

# ── Recommendation Details ─────────────────────────────────
@app.post("/recommendations-details")
async def recommendations_details(request: Request, current_user: UserInDB = Depends(get_current_active_user)):
    body = await request.json()
    category = body.get("category", "home")
    budget = body.get("budget", 0)
    preferences = body.get("preferences", {})

    prompt = f"""
    You are PocketSmart AI, a budget recommendation expert.
    Category: {category}
    Budget: ₹{budget}
    Preferences: {preferences}

    Provide detailed product recommendations with:
    - Product name
    - Price in INR
    - Platform (Amazon/Flipkart/IKEA/Swiggy/Zomato)
    - Direct search URL
    - Why it fits the budget and preference

    Be specific and practical. Stay within budget.
    """

    response = generate_content(contents=prompt)

    # Save to this user's history
    history_entry = {
        "id": str(uuid.uuid4()),
        "category": category,
        "budget": budget,
        "preferences": preferences,
        "result": response.text,
        "timestamp": datetime.utcnow().isoformat()
    }
    recommendation_history[current_user.username].append(history_entry)

    return {"recommendations": response.text, "id": history_entry["id"]}


# ── Main Entry Point ───────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)