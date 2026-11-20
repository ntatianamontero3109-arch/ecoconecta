import base64, hashlib, hmac, secrets, os
from datetime import timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .models import User, SessionToken, now

bearer = HTTPBearer(auto_error=False)

def hash_password(password: str):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 310000)
    return f'pbkdf2_sha256$310000${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}'

def verify_password(password: str, stored: str):
    try:
        alg, rounds, salt, digest = stored.split('$')
        if alg != 'pbkdf2_sha256': return False
        candidate = hashlib.pbkdf2_hmac('sha256', password.encode(), base64.b64decode(salt), int(rounds))
        return hmac.compare_digest(candidate, base64.b64decode(digest))
    except (ValueError, TypeError): return False

def make_token(db: Session, user: User):
    raw = secrets.token_urlsafe(40)
    days = int(os.getenv('SESSION_DAYS', '7'))
    db.add(SessionToken(user_id=user.id, token_hash=hashlib.sha256(raw.encode()).hexdigest(), expires_at=now()+timedelta(days=days)))
    db.commit()
    return raw

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if not credentials: raise HTTPException(401, 'Inicia sesión para continuar')
    token_hash = hashlib.sha256(credentials.credentials.encode()).hexdigest()
    session = db.query(SessionToken).filter_by(token_hash=token_hash).first()
    if not session or session.expires_at.replace(tzinfo=session.expires_at.tzinfo or now().tzinfo) < now():
        raise HTTPException(401, 'La sesión expiró')
    user = db.get(User, session.user_id)
    if not user or not user.active: raise HTTPException(401, 'Cuenta inactiva')
    return user

def roles(*allowed):
    def guard(user: User = Depends(current_user)):
        if user.role not in allowed: raise HTTPException(403, 'No tienes permisos para esta acción')
        return user
    return guard
