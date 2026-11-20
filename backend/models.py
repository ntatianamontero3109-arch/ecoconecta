from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, Text, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

def now(): return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(32))
    password_hash: Mapped[str] = mapped_column(String(300))
    role: Mapped[str] = mapped_column(String(32), index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_pilot: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class SessionToken(Base):
    __tablename__ = 'session_tokens'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class CollectionRequest(Base):
    __tablename__ = 'collection_requests'
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    requester_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    coordinator_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'))
    collector_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'))
    waste_type: Mapped[str] = mapped_column(String(16), index=True)
    generator_type: Mapped[str] = mapped_column(String(20))
    address: Mapped[str] = mapped_column(String(240))
    contact: Mapped[str] = mapped_column(String(100))
    preferred_schedule: Mapped[str] = mapped_column(String(120))
    notes: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(24), default='recibida', index=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    material_kg: Mapped[float | None] = mapped_column(Numeric(10, 2))
    points_awarded: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    requester = relationship('User', foreign_keys=[requester_id])
    coordinator = relationship('User', foreign_keys=[coordinator_id])
    collector = relationship('User', foreign_keys=[collector_id])

class RequestEvent(Base):
    __tablename__ = 'request_events'
    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey('collection_requests.id'), index=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    action: Mapped[str] = mapped_column(String(80))
    detail: Mapped[str] = mapped_column(Text, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class PointRule(Base):
    __tablename__ = 'point_rules'
    id: Mapped[int] = mapped_column(primary_key=True)
    waste_type: Mapped[str] = mapped_column(String(16), unique=True)
    points_per_kg: Mapped[int] = mapped_column(Integer, default=10)
    validated_by_fsd: Mapped[bool] = mapped_column(Boolean, default=False)

class PointEntry(Base):
    __tablename__ = 'point_entries'
    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey('collection_requests.id'), unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    points: Mapped[int] = mapped_column(Integer)
    formula: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Article(Base):
    __tablename__ = 'articles'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(180))
    category: Mapped[str] = mapped_column(String(60))
    body: Mapped[str] = mapped_column(Text)
    published: Mapped[bool] = mapped_column(Boolean, default=True)

class MessageLog(Base):
    __tablename__ = 'message_logs'
    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey('collection_requests.id'))
    kind: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(40))
    detail: Mapped[str] = mapped_column(Text, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
