import os
import logging
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

# Only active, supported Groq models (all old decommissioned models removed)
VALID_GROQ_MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "gemma2-9b-it",
]


def _get_api_key() -> str:
    key = settings.GROQ_API_KEY.strip() if settings.GROQ_API_KEY else ""
    if not key:
        key = os.environ.get("GROQ_API_KEY", "").strip()
    return key


def get_bot_reply(conversation_history: list[dict]) -> str:
    """
    Send the conversation history to Groq and return the assistant reply.
    """
    api_key = _get_api_key()
    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured. Please set GROQ_API_KEY in Render environment settings.")

    client = Groq(api_key=api_key)
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
            logger.error(f"Groq authentication failed: {auth_err}")
            raise ValueError(
                "Invalid Groq API Key. Please generate a new key on console.groq.com and update GROQ_API_KEY in Render."
            ) from auth_err
        except Exception as exc:
            logger.warning(f"Groq model {model_name} failed: {exc}")
            if first_error is None:
                first_error = exc
            continue

    if first_error:
        raise first_error
    raise RuntimeError("No Groq models could respond. Please check your Groq API key and account status.")


