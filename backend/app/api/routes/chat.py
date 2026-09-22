import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.deps import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.session import Session as ChatSession
from app.models.message import Message, MessageRole
from app.schemas.chat import ChatRequest, ChatResponse, HistoryResponse, MessageOut, SessionOut
from app.services.classifier import is_medical_query, OUT_OF_SCOPE_REPLY
from app.services.claude import get_bot_reply

router = APIRouter(prefix="/api/chat", tags=["chat"])


# ── Helper ────────────────────────────────────────────────────────────────────

def _build_history(messages: list[Message]) -> list[dict]:
    """Convert DB messages into the format Claude expects."""
    role_map = {MessageRole.user: "user", MessageRole.bot: "assistant"}
    return [{"role": role_map[m.role], "content": m.content} for m in messages]


def _derive_title(first_user_message: str) -> str:
    """Use the first 60 chars of the opening message as the session title."""
    title = first_user_message.strip().replace("\n", " ")
    return title[:60] + ("…" if len(title) > 60 else "")


# ── POST /api/chat ────────────────────────────────────────────────────────────

@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def send_message(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Send a message and get MedBot's reply.

    - If `session_id` is omitted, a new chat session is created automatically.
    - Domain classification runs before hitting the Claude API.
    """
    # ── 1. Resolve or create session ──────────────────────────────────────────
    if payload.session_id:
        chat_session = db.execute(
            select(ChatSession).where(
                ChatSession.id == payload.session_id,
                ChatSession.user_id == current_user.id,
            )
        ).scalar_one_or_none()

        if chat_session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or does not belong to you.",
            )
    else:
        chat_session = ChatSession(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            title=_derive_title(payload.message),
        )
        db.add(chat_session)
        db.flush()  # get the id without committing yet

    # ── 2. Domain classification ──────────────────────────────────────────────
    is_medical, refusal = is_medical_query(payload.message)

    # ── 3. Persist the user message ───────────────────────────────────────────
    user_msg = Message(
        id=str(uuid.uuid4()),
        session_id=chat_session.id,
        role=MessageRole.user,
        content=payload.message,
    )
    db.add(user_msg)
    db.flush()

    # ── 4. Generate the bot reply ─────────────────────────────────────────────
    if not is_medical:
        bot_reply_text = refusal or OUT_OF_SCOPE_REPLY
    else:
        # Fetch full history for context (excluding the message we just flushed
        # since it's not committed — we'll append it manually)
        prior_messages = db.execute(
            select(Message)
            .where(Message.session_id == chat_session.id, Message.id != user_msg.id)
            .order_by(Message.timestamp)
        ).scalars().all()

        history = _build_history(prior_messages)
        history.append({"role": "user", "content": payload.message})

        try:
            bot_reply_text = get_bot_reply(history)
        except Exception as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"LLM service error: {exc}",
            )

    # ── 5. Persist the bot message ────────────────────────────────────────────
    bot_msg = Message(
        id=str(uuid.uuid4()),
        session_id=chat_session.id,
        role=MessageRole.bot,
        content=bot_reply_text,
    )
    db.add(bot_msg)
    db.commit()
    db.refresh(bot_msg)
    db.refresh(chat_session)

    return ChatResponse(
        session_id=chat_session.id,
        session_title=chat_session.title,
        reply=bot_reply_text,
        message=MessageOut.model_validate(bot_msg),
    )


# ── GET /api/chat/history/:session_id ─────────────────────────────────────────

@router.get("/history/{session_id}", response_model=HistoryResponse)
def get_history(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch all messages for a given session (must belong to the caller)."""
    chat_session = db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        )
    ).scalar_one_or_none()

    if chat_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or does not belong to you.",
        )

    messages = db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.timestamp)
    ).scalars().all()

    return HistoryResponse(
        session=SessionOut.model_validate(chat_session),
        messages=[MessageOut.model_validate(m) for m in messages],
    )


# ── GET /api/chat/sessions ────────────────────────────────────────────────────

@router.get("/sessions", response_model=list[SessionOut])
def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all chat sessions for the authenticated user, newest first."""
    sessions = db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.created_at.desc())
    ).scalars().all()

    return [SessionOut.model_validate(s) for s in sessions]


# ── DELETE /api/chat/:session_id ──────────────────────────────────────────────

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a session and all its messages (cascaded at DB level)."""
    chat_session = db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        )
    ).scalar_one_or_none()

    if chat_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or does not belong to you.",
        )

    db.delete(chat_session)
    db.commit()
