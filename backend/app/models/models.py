import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class PostStatus(str, PyEnum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"

class Platform(str, PyEnum):
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    avatar_url = Column(String(512))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    campaigns = relationship("Campaign", back_populates="user")
    connections = relationship("PlatformConnection", back_populates="user")

class PlatformConnection(Base):
    __tablename__ = "platform_connections"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    platform = Column(Enum(Platform), nullable=False)
    platform_user_id = Column(String(255))
    access_token = Column(Text)
    refresh_token = Column(Text)
    expires_at = Column(DateTime)
    profile_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="connections")

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    business_context = Column(JSON)
    platforms = Column(JSON, default=list)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="campaigns")
    posts = relationship("Post", back_populates="campaign", cascade="all, delete-orphan")

class Post(Base):
    __tablename__ = "posts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    platform = Column(Enum(Platform), nullable=False)
    content = Column(Text, nullable=False)
    media_urls = Column(JSON, default=list)
    scheduled_for = Column(DateTime)
    published_at = Column(DateTime)
    status = Column(Enum(PostStatus), default=PostStatus.DRAFT)
    platform_post_id = Column(String(255))
    engagement = Column(JSON)
    ai_metadata = Column(JSON)
    series_id = Column(String(100))
    series_order = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    campaign = relationship("Campaign", back_populates="posts")
