"""
LLM service — uses Groq's OpenAI-compatible API with llama-3.3-70b-versatile.
"""

from groq import Groq

from app.core.config import settings

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

_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client


def get_bot_reply(conversation_history: list[dict]) -> str:
    """
    Send the conversation history to Groq and return the assistant reply.

    `conversation_history` is a list of dicts:
        { "role": "user" | "assistant", "content": "<text>" }
    """
    client = _get_client()

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=messages,
        max_tokens=1024,
        temperature=0.7,
    )

    return response.choices[0].message.content
