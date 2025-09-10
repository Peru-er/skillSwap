from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session


from src.database.models import User, Skill, Exchange, user_skills
from src.schemas import UserCreate, UserUpdate


async def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Отримати список користувачів з пагінацією."""
    return db.query(User).offset(skip).limit(limit).all()


async def get_user(db: Session, user_id: int) -> Optional[User]:
    """Отримати користувача за його ID."""
    return db.query(User).filter(User.id == user_id).first()


async def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Отримати користувача за email."""
    return db.query(User).filter(User.email == email).first()


async def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Отримати користувача за username."""
    return db.query(User).filter(User.username == username).first()


async def create_user(db: Session, user: UserCreate) -> User:
    """Створити нового користувача."""
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


async def update_user(
    db: Session,
    user_id: int,
    user_update: UserUpdate
) -> Optional[User]:
    """Оновити дані користувача."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
    return db_user


async def get_user_skills(db: Session, user_id: int) -> Optional[List]:
    """Отримати всі навички користувача за ID."""
    user = db.query(User).filter(User.id == user_id).first()
    return user.skills if user else None

async def get_top_skills(db: Session):
    results = (
        db.query(Skill.title, func.count(user_skills.c.user_id).label("count"))
        .join(user_skills, Skill.id == user_skills.c.skill_id)
        .group_by(Skill.id)
        .order_by(func.count(user_skills.c.user_id).desc())
        .limit(10)
        .all()
    )
    return [{"skill": r[0], "users_count": r[1]} for r in results]

# Найактивніші користувачі
async def get_active_users(db: Session):
    results = (
        db.query(
            User.username,
            func.count(Exchange.id).label("exchanges_count")
        )
        .join(Exchange, (Exchange.sender_id == User.id) | (Exchange.receiver_id == User.id))
        .group_by(User.id)
        .order_by(func.count(Exchange.id).desc())
        .limit(10)
        .all()
    )
    return [{"username": r[0], "exchanges_count": r[1]} for r in results]

# Відсоток успішних обмінів
async def get_exchange_success_rate(db: Session):
    total = db.query(func.count(Exchange.id)).scalar()
    completed = db.query(func.count(Exchange.id)).filter(Exchange.status == "completed").scalar()
    success_rate = (completed / total * 100) if total else 0
    return {"success_rate": round(success_rate, 2)}

