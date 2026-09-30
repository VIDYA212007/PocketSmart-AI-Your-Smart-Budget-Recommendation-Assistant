from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
from google import genai
from dotenv import load_dotenv
from state import recommendation_history
from auth import get_current_active_user
from models import UserInDB
import os, uuid
import os, uuid
from datetime import datetime

load_dotenv()
router = APIRouter()
templates = Jinja2Templates(directory="templates")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
PRIMARY_MODEL = os.getenv("GEMINI_PARTY_MODEL") or os.getenv("GEMINI_MODEL") or "gemini-3.5-flash-lite"
FALLBACK_MODEL = os.getenv("GEMINI_PARTY_FALLBACK_MODEL") or os.getenv("GEMINI_FALLBACK_MODEL") or "gemini-3.8-flash"


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

class PartyRequest(BaseModel):
    budget: float
    event_type: str
    guests: str
    location: Optional[str] = "Home"
    food_preference: Optional[str] = ""
    includes: Optional[List[str]] = []
    notes: Optional[str] = ""

def get_party_recommendations(budget, event_type, guests, location, food_preference, includes, notes):
    includes_str = ", ".join(includes) if includes else "Catering, Decoration"
    prompt = f"""
You are an expert party and event budget planner for India.

Generate a detailed party budget plan for:
- Total Budget: Rs.{budget}
- Event Type: {event_type}
- Number of Guests: {guests}
- Venue Type: {location}
- Food Preference: {food_preference or 'No preference'}
- Party Needs: {includes_str}
- Special Requests: {notes or 'None'}

Return ONLY a valid JSON object in this exact format (no markdown, no explanation outside JSON):
{{
  "categories": [
    {{
      "name": "Venue",
      "icon": "📍",
      "allocation": 0,
      "items": [
        {{
          "name": "Home venue",
          "description": "Utilizing the home as the venue.",
          "price": 0
        }}
      ]
    }},
    {{
      "name": "Catering",
      "icon": "🍽️",
      "allocation": 15000,
      "items": [
        {{
          "name": "Home-cooked meal",
          "description": "Simple home-cooked meal for {guests} guests.",
          "price": 15000
        }}
      ]
    }}
  ],
  "venues": [
    {{
      "name": "Home",
      "type": "Residential",
      "location": "{location}",
      "cost": 0
    }}
  ],
  "tips": [
    "Book catering at least 2 weeks in advance for better rates",
    "Buy decorations in bulk from wholesale markets for savings"
  ]
}}

Rules:
- Create categories only for the party needs: {includes_str}
- Add a Contingency category (5-10% of budget) for unexpected expenses
- All prices must be realistic for India in 2024-25 in INR
- Sum of all allocations must equal exactly Rs.{budget}
- Venue suggestions should match: {location}
- Return ONLY the JSON, nothing else
"""
    response = generate_content(contents=prompt)
    return response.text

@router.get("/party-planner")
async def party_planner_page(request: Request, current_user: UserInDB = Depends(get_current_active_user)):
    return templates.TemplateResponse("party_planner.html", {"request": request, "user": current_user})

@router.post("/generate-party")
async def generate_party(data: PartyRequest, current_user: UserInDB = Depends(get_current_active_user)):
    try:
        recommendations = get_party_recommendations(
            data.budget, data.event_type, data.guests,
            data.location, data.food_preference, data.includes, data.notes
        )
        recommendation_history[current_user.username].append({
            "id": str(uuid.uuid4()),
            "category": "party",
            "budget": data.budget,
            "preferences": {
                "event_type": data.event_type,
                "guests": data.guests,
                "location": data.location,
                "includes": data.includes
            },
            "result": recommendations,
            "timestamp": datetime.utcnow().isoformat()
        })
        return {"recommendations": recommendations, "budget": data.budget}
    except Exception as e:
        return {"detail": f"AI generation failed: {str(e)}"}
