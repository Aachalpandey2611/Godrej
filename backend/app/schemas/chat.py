from datetime import datetime
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None  # if None, a new session is created


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    timestamp: datetime

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    session_id: str
    session_title: str
    reply: str
    message: MessageOut   # the bot message that was just saved


class SessionOut(BaseModel):
    id: str
    title: str
    created_at: datetime

    model_config = {"from_attributes": True}


class HistoryResponse(BaseModel):
    session: SessionOut
    messages: list[MessageOut]
