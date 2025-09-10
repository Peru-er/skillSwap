
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database.db import get_db
from src import repository

router = APIRouter(
    prefix='/api/stats',
    tags=['Stats']
)

@router.get('/top-skills')
def top_skills(db: Session = Depends(get_db)):
    return repository.stats.get_top_skills(db)

@router.get('/active-users')
def active_users(db: Session = Depends(get_db)):
    return repository.stats.get_active_users(db)

@router.get('/exchange-success-rate')
def exchange_success_rate(db: Session = Depends(get_db)):
    return repository.stats.get_exchange_success_rate(db)

