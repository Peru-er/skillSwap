
import enum
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey,
    Table, Text, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database.db import Base


# --- Association table ---
skill_user_association = Table(
    "skill_user_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("skill_id", Integer, ForeignKey("skills.id", ondelete="CASCADE"))
)


# --- Enums ---
class SkillLevel(enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"


class ExchangeStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    completed = "completed"
    cancelled = "cancelled"


# --- Models ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100))
    bio = Column(Text)
    avatar_url = Column(String(255))
    phone = Column(String(20))
    location = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    skills = relationship("Skill", secondary=skill_user_association, back_populates="users")
    sent_exchanges = relationship("Exchange", foreign_keys="Exchange.sender_id", back_populates="sender")
    received_exchanges = relationship("Exchange", foreign_keys="Exchange.receiver_id", back_populates="receiver")
    given_reviews = relationship("Review", foreign_keys="Review.reviewer_id", back_populates="reviewer")
    received_reviews = relationship("Review", foreign_keys="Review.reviewed_id", back_populates="reviewed")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    level = Column(SQLEnum(SkillLevel), nullable=False)
    can_teach = Column(Boolean, default=False)
    want_learn = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    users = relationship("User", secondary=skill_user_association, back_populates="skills")
    exchanges = relationship("Exchange", back_populates="skill")


class Exchange(Base):
    __tablename__ = "exchanges"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    message = Column(Text)
    status = Column(SQLEnum(ExchangeStatus), default=ExchangeStatus.pending)
    hours_proposed = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_exchanges")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_exchanges")
    skill = relationship("Skill", back_populates="exchanges")
    reviews = relationship("Review", back_populates="exchange")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    exchange_id = Column(Integer, ForeignKey("exchanges.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewed_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    exchange = relationship("Exchange", back_populates="reviews")
    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="given_reviews")
    reviewed = relationship("User", foreign_keys=[reviewed_id], back_populates="received_reviews")

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    skills = relationship('Skill', back_populates='category')

