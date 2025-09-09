
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import SkillCreate, SkillUpdate, SkillResponse
from src.repository import skills as repository_skills


router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/", response_model=List[SkillResponse])
async def read_skills(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    can_teach: Optional[bool] = None,
    want_learn: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Отримати список навичок з можливістю фільтрації.


    - **skip**: кількість записів для пропуску
    - **limit**: максимальна кількість записів
    - **category**: фільтр за категорією
    - **can_teach**: показати тільки тих, хто може навчати
    - **want_learn**: показати тільки тих, хто хоче вчитися
    - **search**: пошук за назвою або описом
    """
    return await repository_skills.get_skills(
        db, skip, limit, category, can_teach, want_learn, search
    )


@router.get("/{skill_id}", response_model=SkillResponse)
async def read_skill(skill_id: int, db: Session = Depends(get_db)):
    """Отримати детальну інформацію про навичку."""
    skill = await repository_skills.get_skill(db, skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Навичка з ID {skill_id} не знайдена"
        )
    return skill


@router.post("/", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    skill: SkillCreate,
    user_id: int = 1,  # Тимчасово, поки немає автентифікації
    db: Session = Depends(get_db)
):
    """Створити нову навичку."""
    return await repository_skills.create_skill(db, skill, user_id)


@router.put("/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: int,
    skill_update: SkillUpdate,
    db: Session = Depends(get_db)
):
    """Оновити існуючу навичку."""
    skill = await repository_skills.update_skill(db, skill_id, skill_update)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Навичка з ID {skill_id} не знайдена"
        )
    return skill


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    """Видалити навичку."""
    skill = await repository_skills.delete_skill(db, skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Навичка з ID {skill_id} не знайдена"
        )
    return None


@router.get("/{skill_id}/matches")
async def find_matches(skill_id: int, db: Session = Depends(get_db)):
    """Знайти потенційні збіги для обміну навичками."""
    matches = await repository_skills.find_skill_matches(db, skill_id)
    if not matches["skill"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Навичка з ID {skill_id} не знайдена"
        )
    return matches

