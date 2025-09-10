
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from datetime import date


from src.database.db import get_db
from src.schemas import ExchangeCreate, ExchangeUpdate, ExchangeResponse, ExchangeStatus
from src.repository import exchanges as repository_exchanges
from src import repository


router = APIRouter(prefix='/exchanges', tags=["exchanges"])


@router.get("/", response_model=List[ExchangeResponse])
async def read_exchanges(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[ExchangeStatus] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Отримати список обмінів з фільтрацією.


    - **status_filter**: фільтр за статусом (pending, accepted, etc.)
    - **user_id**: показати обміни конкретного користувача
    """
    exchanges = await repository_exchanges.get_exchanges(
        db, skip, limit, status_filter, user_id
    )
    return exchanges


@router.get("/{exchange_id}", response_model=ExchangeResponse)
async def read_exchange(exchange_id: int, db: Session = Depends(get_db)):
    """Отримати деталі обміну."""
    exchange = await repository_exchanges.get_exchange(db, exchange_id)
    if exchange is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Обмін з ID {exchange_id} не знайдено"
        )
    return exchange


@router.post("/", response_model=ExchangeResponse, status_code=status.HTTP_201_CREATED)
async def create_exchange(
    exchange: ExchangeCreate,
    sender_id: int = 1,  # Тимчасово, поки немає автентифікації
    db: Session = Depends(get_db)
):
    """Створити запит на обмін навичками."""
    # Перевіряємо, чи не намагається користувач створити обмін сам з собою
    if sender_id == exchange.receiver_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не можна створити обмін з самим собою"
        )

    return await repository_exchanges.create_exchange(db, exchange, sender_id)


@router.put("/{exchange_id}", response_model=ExchangeResponse)
async def update_exchange_status(
    exchange_id: int,
    exchange_update: ExchangeUpdate,
    current_user_id: int = 1,  # Тимчасово
    db: Session = Depends(get_db)
):
    """Оновити статус обміну (прийняти/відхилити)."""
    exchange = await repository_exchanges.update_exchange(
        db, exchange_id, exchange_update, current_user_id
    )
    if exchange is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Обмін з ID {exchange_id} не знайдено"
        )
    return exchange


@router.get("/my/sent", response_model=List[ExchangeResponse])
async def read_my_sent_exchanges(
    user_id: int = 1,  # Тимчасово
    db: Session = Depends(get_db)
):
    """Отримати надіслані запити на обмін."""
    return await repository_exchanges.get_user_sent_exchanges(db, user_id)


@router.get("/my/received", response_model=List[ExchangeResponse])
async def read_my_received_exchanges(
    user_id: int = 1,  # Тимчасово
    db: Session = Depends(get_db)
):
    """Отримати отримані запити на обмін."""
    return await repository_exchanges.get_user_received_exchanges(db, user_id)

@router.get('/')
def get_exchanges(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    sort_order: str = Query('desc', regex='^(asc|desc)$'),
    db: Session = Depends(get_db)
):
    return repository.exchanges.get_filtered_exchanges(
        db=db,
        from_date=from_date,
        to_date=to_date,
        status=status,
        user_id=user_id,
        sort_order=sort_order
    )
