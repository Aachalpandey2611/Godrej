import logging
from groq import Groq

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

FALLBACK_MODELS = [
    "llama-3.1-8b-instant",
    "llama3-8b-8192",
    "llama-3.3-70b-versatile",
    "gemma2-9b-it",
    "mixtral-8x7b-32768",
]


def _get_client() -> Groq:
    api_key = settings.GROQ_API_KEY.strip() if settings.GROQ_API_KEY else ""
    return Groq(api_key=api_key)


def get_bot_reply(conversation_history: list[dict]) -> str:
    """
    Send the conversation history to Groq and return the assistant reply.
    Automatically tries fallback models if the primary model fails or is unavailable.
    """
    client = _get_client()
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

    models_to_try = []
    if settings.GROQ_MODEL and settings.GROQ_MODEL.strip():
        models_to_try.append(settings.GROQ_MODEL.strip())
    for m in FALLBACK_MODELS:
        if m not in models_to_try:
            models_to_try.append(m)

    last_error = None
    for model_name in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=1024,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as exc:
            logger.warning(f"Groq model {model_name} failed: {exc}")
            last_error = exc
            continue

    if last_error:
        raise last_error
    raise RuntimeError("No Groq models available or API call failed.")

