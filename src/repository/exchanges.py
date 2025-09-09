
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_


from src.database.models import Exchange, User, Skill
from src.schemas import ExchangeCreate, ExchangeUpdate, ExchangeStatus


async def get_exchanges(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[ExchangeStatus] = None,
    user_id: Optional[int] = None
) -> List[Exchange]:
    """Отримати список обмінів з фільтрацією."""
    query = db.query(Exchange)

    if status_filter:
        query = query.filter(Exchange.status == status_filter.value)

    if user_id:
        query = query.filter(
            or_(
                Exchange.sender_id == user_id,
                Exchange.receiver_id == user_id
            )
        )

    return query.offset(skip).limit(limit).all()


async def get_exchange(db: Session, exchange_id: int) -> Optional[Exchange]:
    """Отримати обмін за ID."""
    return db.query(Exchange).filter(Exchange.id == exchange_id).first()


async def create_exchange(
    db: Session,
    exchange: ExchangeCreate,
    sender_id: int
) -> Optional[Exchange]:
    """Створити новий запит на обмін."""
    # Перевіряємо, чи існують користувачі та навичка
    sender = db.query(User).filter(User.id == sender_id).first()
    receiver = db.query(User).filter(User.id == exchange.receiver_id).first()
    skill = db.query(Skill).filter(Skill.id == exchange.skill_id).first()

    if not all([sender, receiver, skill]):
        return None

    db_exchange = Exchange(
        sender_id=sender_id,
        receiver_id=exchange.receiver_id,
        skill_id=exchange.skill_id,
        message=exchange.message,
        hours_proposed=exchange.hours_proposed,
        status=ExchangeStatus.pending.value
    )

    db.add(db_exchange)
    db.commit()
    db.refresh(db_exchange)
    return db_exchange


async def update_exchange(
    db: Session,
    exchange_id: int,
    exchange_update: ExchangeUpdate,
    current_user_id: int
) -> Optional[Exchange]:
    """Оновити статус обміну."""
    db_exchange = db.query(Exchange).filter(Exchange.id == exchange_id).first()

    if not db_exchange:
        return None

    # Перевіряємо, чи користувач має право оновлювати цей обмін
    if exchange_update.status in [ExchangeStatus.accepted, ExchangeStatus.rejected]:
        # Тільки отримувач може прийняти або відхилити
        if db_exchange.receiver_id != current_user_id:
            return None
    elif exchange_update.status == ExchangeStatus.cancelled:
        # Скасувати може будь-хто з учасників
        if current_user_id not in [db_exchange.sender_id, db_exchange.receiver_id]:
            return None

    # Оновлюємо статус
    db_exchange.status = exchange_update.status.value
    if exchange_update.message:
        db_exchange.message = exchange_update.message

    db.commit()
    db.refresh(db_exchange)
    return db_exchange


async def get_user_sent_exchanges(db: Session, user_id: int) -> List[Exchange]:
    """Отримати надіслані користувачем запити."""
    return db.query(Exchange).filter(Exchange.sender_id == user_id).all()


async def get_user_received_exchanges(db: Session, user_id: int) -> List[Exchange]:
    """Отримати отримані користувачем запити."""
    return db.query(Exchange).filter(Exchange.receiver_id == user_id).all()


