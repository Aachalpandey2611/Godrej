from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.security import decode_access_token
from app.db.database import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)

GUEST_USER_ID = "00000000-0000-0000-0000-000000000001"
GUEST_EMAIL   = "guest@medichat.app"
GUEST_NAME    = "Guest"


def _get_or_create_guest(db: Session) -> User:
    """Return the shared guest user, creating it if it doesn't exist."""
    user = db.get(User, GUEST_USER_ID)
    if user is None:
        user = User(
            id=GUEST_USER_ID,
            email=GUEST_EMAIL,
            name=GUEST_NAME,
            hashed_password="",   # no password for guest
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    # No token → return guest user
    if credentials is None:
        return _get_or_create_guest(db)

    token = credentials.credentials
    user_id = decode_access_token(token)

    if user_id is None:
        return _get_or_create_guest(db)

    user = db.get(User, user_id)
    if user is None:
        return _get_or_create_guest(db)

    return user
