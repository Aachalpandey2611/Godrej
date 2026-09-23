import os
import logging
import httpx
from groq import Groq, AuthenticationError

from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are MedBot, a medical information assistant.

Rules you must follow at all times:
- Only answer questions related to medicine, health, symptoms, treatments, medications, and anatomy.
- If a question is unrelated to medicine (e.g. coding, sports, finance, entertainment), politely decline and explain that you only handle medical topics.
- ALWAYS end every response with this exact disclaimer on a new line:
  > ⚠️ *This is not a substitute for professional medical advice. Consult a qualified healthcare provider for diagnosis and treatment.*
- Do NOT provide specific drug dosages or definitive diagnoses — encourage the user to consult a licensed doctor for those.
- Be empathetic, clear, and concise. Use plain language that a non-medical person can understand.
- When appropriate, suggest seeking emergency care (call 911 or visit the nearest ER) for life-threatening situations.
"""

# Only active, supported Groq models
VALID_GROQ_MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "gemma2-9b-it",
]

# Supported Gemini models
GEMINI_MODELS = [
    "gemini-1.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-pro",
]


def _get_gemini_key() -> str:
    key = settings.GEMINI_API_KEY.strip() if settings.GEMINI_API_KEY else ""
    if not key:
        key = os.environ.get("GEMINI_API_KEY", "").strip() or os.environ.get("GOOGLE_API_KEY", "").strip()
    return key


def _get_groq_key() -> str:
    key = settings.GROQ_API_KEY.strip() if settings.GROQ_API_KEY else ""
    if not key:
        key = os.environ.get("GROQ_API_KEY", "").strip()
    return key


def _call_gemini(conversation_history: list[dict], gemini_key: str) -> str:
    """Call Google Gemini REST API using httpx."""
    # Convert chat history into Gemini contents format
    contents = []
    for msg in conversation_history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}],
        })

    last_err = None
    for model in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
        payload = {
            "system_instruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1024,
            }
        }
        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
                else:
                    logger.warning(f"Gemini {model} returned {res.status_code}: {res.text}")
                    last_err = Exception(f"Gemini API returned {res.status_code}: {res.text}")
        except Exception as e:
            logger.warning(f"Gemini {model} call failed: {e}")
            last_err = e
            continue

    if last_err:
        raise last_err
    raise RuntimeError("Gemini API call failed.")


def _call_groq(conversation_history: list[dict], groq_key: str) -> str:
    """Call Groq API with valid models."""
    client = Groq(api_key=groq_key)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

    models_to_try = []
    if settings.GROQ_MODEL and settings.GROQ_MODEL.strip() in VALID_GROQ_MODELS:
        models_to_try.append(settings.GROQ_MODEL.strip())
    for m in VALID_GROQ_MODELS:
        if m not in models_to_try:
            models_to_try.append(m)

    first_error = None
    for model_name in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=1024,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except AuthenticationError as auth_err:
            logger.error(f"Groq auth error: {auth_err}")
            raise ValueError(
                "Invalid Groq API Key. Please check GROQ_API_KEY in Render."
            ) from auth_err
        except Exception as exc:
            logger.warning(f"Groq model {model_name} failed: {exc}")
            if first_error is None:
                first_error = exc
            continue

    if first_error:
        raise first_error
    raise RuntimeError("No Groq models could respond.")


def get_bot_reply(conversation_history: list[dict]) -> str:
    """
    Send the conversation history to Gemini or Groq and return the reply.
    Prefers Gemini if GEMINI_API_KEY is present, falls back to Groq or vice versa.
    """
    gemini_key = _get_gemini_key()
    groq_key = _get_groq_key()

    if not gemini_key and not groq_key:
        raise ValueError("Neither GEMINI_API_KEY nor GROQ_API_KEY is configured in Render environment variables.")

    # 1. Try Gemini if key exists
    if gemini_key:
        try:
            return _call_gemini(conversation_history, gemini_key)
        except Exception as e:
            logger.warning(f"Gemini failed, trying Groq fallback if available: {e}")
            if not groq_key:
                raise e

    # 2. Try Groq if key exists
    if groq_key:
        return _call_groq(conversation_history, groq_key)

    raise RuntimeError("Unable to generate response from AI providers.")



