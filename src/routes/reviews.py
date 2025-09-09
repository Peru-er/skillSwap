
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session


from src.database.db import get_db
from src.schemas import ReviewCreate, ReviewResponse
from src.repository import reviews as repository_reviews


router = APIRouter(prefix='/reviews', tags=["reviews"])


@router.get("/", response_model=List[ReviewResponse])
async def read_reviews(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Отримати список відгуків."""
    reviews = await repository_reviews.get_reviews(db, skip, limit, user_id)
    return reviews


@router.get("/{review_id}", response_model=ReviewResponse)
async def read_review(review_id: int, db: Session = Depends(get_db)):
    """Отримати конкретний відгук."""
    review = await repository_reviews.get_review(db, review_id)
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Відгук з ID {review_id} не знайдено"
        )
    return review


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate,
    reviewer_id: int = 1,  # Тимчасово
    db: Session = Depends(get_db)
):
    """Створити відгук після завершеного обміну."""
    # Перевіряємо, чи існує обмін і чи він завершений
    db_review = await repository_reviews.create_review(db, review, reviewer_id)
    if db_review is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не можна створити відгук. Перевірте, чи обмін завершений та чи ви були його учасником"
        )
    return db_review


@router.get("/user/{user_id}", response_model=List[ReviewResponse])
async def read_user_reviews(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Отримати всі відгуки про користувача."""
    reviews = await repository_reviews.get_user_reviews(db, user_id)
    return reviews


@router.get("/user/{user_id}/rating")
async def get_user_rating(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Отримати середній рейтинг користувача."""
    rating_info = await repository_reviews.get_user_rating(db, user_id)
    if rating_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Користувача з ID {user_id} не знайдено"
        )
    return rating_info

