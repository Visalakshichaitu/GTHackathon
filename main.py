from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import os
import re
from typing import Dict, Any, List, Optional
from collections import defaultdict

# ==== Load API key and init Groq client ====
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI()

# Allow all origins (for hackathon demo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
#   CUSTOMER PROFILES
# =========================

# In-memory store for demo; in real life this would be a DB
CUSTOMERS: Dict[str, Dict[str, Any]] = {}


def create_default_customer(customer_id: str, location: str) -> Dict[str, Any]:
    """Create a new default profile."""
    city = extract_city_from_location(location)
    return {
        "id": customer_id,
        "name": None,                         # we will try to detect from message
        "loyalty_tier": "Guest",
        "favorite_items": [],
        "favorite_topics": [],
        "favorite_stores": [],
        "home_location": location or "Unknown",
        "current_city": city or "Unknown",
        "last_location": location or "Unknown",
        "history": [],                        # last messages
        "mood_history": [],
        "frequent_intents": defaultdict(int),
        "notes": "New customer, no prior history.",
    }


NAME_PATTERNS = [
    r"\bmy name is ([A-Za-z]+)",
    r"\bi am ([A-Za-z]+)",
    r"\bi'm ([A-Za-z]+)",
    r"\bthis is ([A-Za-z]+)",
]


def maybe_extract_name(text: str) -> Optional[str]:
    text_lower = text.lower()
    for pat in NAME_PATTERNS:
        m = re.search(pat, text_lower)
        if m:
            # Capitalize first letter
            return m.group(1).strip().title()
    return None


INTEREST_KEYWORDS = {
    "coffee": "coffee",
    "latte": "coffee",
    "tea": "tea",
    "pizza": "pizza",
    "biryani": "biryani",
    "movie": "movies",
    "series": "movies",
    "k-drama": "kdrama",
    "shopping": "shopping",
    "shoes": "fashion",
    "dress": "fashion",
    "mall": "malls",
}


def update_preferences(profile: Dict[str, Any], text: str) -> None:
    text_lower = text.lower()
    for kw, label in INTEREST_KEYWORDS.items():
        if kw in text_lower and label not in profile["favorite_topics"]:
            profile["favorite_topics"].append(label)


def extract_city_from_location(location: str) -> Optional[str]:
    if not location:
        return None
    # very simple heuristic: last token after comma or last word
    if "," in location:
        return location.split(",")[-1].strip().title()
    parts = location.strip().split()
    if not parts:
        return None
    return parts[-1].title()


def detect_mood(message: str) -> Optional[str]:
    text = message.lower()
    if any(w in text for w in ["cold", "freezing", "chilly"]):
        return "cold"
    if any(w in text for w in ["tired", "sleepy", "exhausted"]):
        return "tired"
    if any(w in text for w in ["bored", "boring"]):
        return "bored"
    if any(w in text for w in ["sad", "depressed", "upset"]):
        return "sad"
    if any(w in text for w in ["happy", "excited", "great"]):
        return "happy"
    if any(w in text for w in ["hungry", "starving"]):
        return "hungry"
    return None


def detect_intent(message: str) -> str:
    text = message.lower()

    # order / store / policy type
    if any(w in text for w in ["where is my order", "track", "tracking", "delivery"]):
        return "order_status"
    if any(w in text for w in ["refund", "return", "exchange"]):
        return "refund_policy"
    if any(w in text for w in ["open", "closing time", "close", "store timing"]):
        return "store_info"
    if any(w in text for w in ["size", "in stock", "availability", "stock"]):
        return "product_availability"
    if any(w in text for w in ["near me", "nearby", "closest", "around me"]):
        return "location_help"

    # health / food / mood
    if any(w in text for w in ["headache", "fever", "sick", "health", "medicine"]):
        return "health_advice"
    if any(w in text for w in ["eat", "restaurant", "food", "hungry"]):
        return "food_suggestion"

    # coffee-shop style scenario
    if "cold" in text:
        return "cold_outside"

    # GK and general questions
    if any(w in text for w in ["who is", "what is", "capital of", "when did"]):
        return "general_knowledge"

    # fallback
    return "chit_chat"


def get_customer(customer_id: str, location: str, message: str) -> Dict[str, Any]:
    if customer_id not in CUSTOMERS:
        CUSTOMERS[customer_id] = create_default_customer(customer_id, location)

    profile = CUSTOMERS[customer_id]

    # Try to detect name from this message if not already set
    if profile["name"] is None:
        name = maybe_extract_name(message)
        if name:
            profile["name"] = name

    # Update city from location
    if location:
        profile["last_location"] = location
        city = extract_city_from_location(location)
        if city:
            profile["current_city"] = city

    # Update history
    profile["history"].append(message)
    profile["history"] = profile["history"][-10:]  # keep last 10 messages only

    # Update interests
    update_preferences(profile, message)

    return profile


# =========================
#   RAG DOCS (GENERIC RETAIL)
# =========================

DOCS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Store Timings",
        "location": "any",
        "text": "Most of our partner stores are open from 9 AM to 9 PM, but timings may vary by location. Ask with a specific city or mall name for more accurate timings."
    },
    {
        "id": 2,
        "title": "Order Tracking",
        "location": "any",
        "text": "Orders can be tracked from the 'My Orders' section in the app or website using the order ID. Standard delivery takes 3–5 business days unless express shipping is selected."
    },
    {
        "id": 3,
        "title": "Refund & Returns Policy",
        "location": "any",
        "text": "Most items can be returned within 7–10 days of delivery if unused and with the original bill. Refunds are processed back to the original payment method after quality check."
    },
    {
        "id": 4,
        "title": "Membership & Loyalty",
        "location": "any",
        "text": "Loyal customers may receive personalized coupons, birthday offers, and early access to sales based on their shopping history and favorite categories."
    },
    {
        "id": 5,
        "title": "In-store Help",
        "location": "any",
        "text": "If you are standing outside a store and feel cold, tired, or confused, you can walk in and ask any staff member at the help desk for assistance or a place to sit."
    },
]

# ==== PII masking ====
PII_PATTERNS = [
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}",  # email
    r"\b\d{10}\b",  # 10-digit phone number
]


def mask_pii(text: str) -> str:
    masked = text
    for pat in PII_PATTERNS:
        masked = re.sub(pat, "[SENSITIVE]", masked)
    return masked


# ==== Simple keyword-based RAG retrieval ====
def retrieve_context(message: str, location: str) -> List[Dict[str, Any]]:
    tokens = re.findall(r"\w+", message.lower())
    scores = []
    for doc in DOCS:
        doc_tokens = re.findall(r"\w+", doc["text"].lower())
        overlap = len(set(tokens) & set(doc_tokens))
        loc_score = 1 if (doc["location"] == "any" or doc["location"] == location) else 0
        total = overlap + loc_score
        scores.append((total, doc))
    scores.sort(key=lambda x: x[0], reverse=True)
    top_docs = [d for (s, d) in scores if s > 0][:3]
    return top_docs


# =========================
#   API MODELS
# =========================

class ChatRequest(BaseModel):
    message: str
    customer_id: str
    location: str


class ChatResponse(BaseModel):
    reply: str


# =========================
#   CHAT ENDPOINT
# =========================

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # 1. Mask PII
    masked_message = mask_pii(req.message)

    # 2. Detect intent & mood
    intent = detect_intent(masked_message)
    mood = detect_mood(masked_message)

    # 3. Customer profile (create/update)
    customer = get_customer(req.customer_id, req.location, masked_message)
    customer["frequent_intents"][intent] += 1
    if mood:
        customer["mood_history"].append(mood)
        customer["mood_history"] = customer["mood_history"][-10:]

    # 4. Retrieve docs (RAG) when intent is related to store/order/policy
    docs: List[Dict[str, Any]] = []
    if intent in {"store_info", "order_status", "refund_policy", "product_availability", "location_help", "cold_outside"}:
        docs = retrieve_context(masked_message, req.location)

    context_text = "\n\n".join(
        [f"{d['title']}: {d['text']}" for d in docs]
    ) or "No specific internal documents were found for this question."

    recent_history = " | ".join(customer["history"][-5:]) if customer["history"] else "No prior messages."
    name_for_prompt = customer["name"] or "friend"
    interests = ", ".join(customer["favorite_topics"]) if customer["favorite_topics"] else "not known yet"
    city = customer.get("current_city", "Unknown")

    # Build a short summary of frequent intents
    if customer["frequent_intents"]:
        top_intent = max(customer["frequent_intents"], key=customer["frequent_intents"].get)
    else:
        top_intent = "unknown"

    mood_trend = customer["mood_history"][-1] if customer["mood_history"] else "unknown"

    # 5. Build system prompt
    system_prompt = f"""
You are a hyper-personalized AI Customer Support & Personal Assistant.

You can answer ANY type of question:
- general knowledge (e.g., who is the president of a country),
- lifestyle & food suggestions,
- basic wellness tips (non-medical, always suggest seeing a doctor for serious issues),
- shopping, orders, store timings, refunds, memberships, etc.

You MUST:
- Use the customer's profile, interests, previous messages, and location when helpful.
- Use internal docs (context) for anything related to orders, stores, policies or membership.
- Be specific and actionable. When user is near a store or location, suggest clear next steps.
- Keep answers friendly, concise (2–5 sentences), and easy to read.
- Sound caring and human: reflect their mood gently (if they seem cold, tired, bored, etc.).

Customer profile:
- ID: {customer["id"]}
- Name: {name_for_prompt}
- Loyalty tier: {customer["loyalty_tier"]}
- Home / last known location text: {customer["last_location"]}
- City (rough): {city}
- Known interests: {interests}
- Notes: {customer["notes"]}
- Most common type of question so far: {top_intent}
- Recent mood trend: {mood_trend}

Recent conversation history (most recent last): {recent_history}

If the user says "I'm cold" and mentions or implies they are outside a store or mall, invite them to go inside somewhere nearby (like a cafe, store, or waiting area) and optionally suggest a warm drink or snack.
Never mention that you are masking data or that you are using documents or 'RAG'. Just answer naturally.
""".strip()

    # 6. Build user prompt with RAG context + intent + mood
    user_prompt = f"""
User message (PII masked): {masked_message}

Detected intent: {intent}
Detected mood: {mood or "unknown"}

Relevant internal documents (for store/order/policy context, if any):
{context_text}

Now respond with a friendly, short answer that feels personal to {name_for_prompt}.
You should:
- Acknowledge their location when relevant (they wrote: "{req.location}").
- Use their interests when suggesting food, places, or activities.
- If intent is general_knowledge, give a clear, correct answer plus a tiny personal touch.
- If intent is health_advice, give only general self-care tips and advise consulting a doctor for serious issues.
- If intent is order_status/store_info/refund_policy/product_availability/location_help or cold_outside, use the internal docs when possible and give very actionable next steps.
- If chit_chat, talk like a warm friend who remembers their preferences.
""".strip()

    # 7. Call Groq LLM
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    reply = completion.choices[0].message.content
    return ChatResponse(reply=reply)
