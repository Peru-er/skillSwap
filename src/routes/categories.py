
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.database.db import get_db
from src.schemas import Category, CategoryCreate
from src.repository import categories

router = APIRouter(
    prefix='/api/categories',
    tags=['Categories']
)

@router.post('/', response_model=Category)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    return categories.create_category(db, category)

@router.get('/', response_model=List[Category])
def list_categories(db: Session = Depends(get_db)):
    return categories.get_categories(db)

@router.get('/{category_id}', response_model=Category)
def get_category(category_id: int, db: Session = Depends(get_db)):
    db_category = categories.get_category(db, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail='Category not found')
    return db_category

@router.put('/{category_id}', response_model=Category)
def update_category(category_id: int, category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = categories.update_category(db, category_id, category.name)
    if not db_category:
        raise HTTPException(status_code=404, detail='Category not found')
    return db_category

@router.delete('/{category_id}')
def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_category = categories.delete_category(db, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail='Category not found')
    return {'message': 'Category deleted'}

