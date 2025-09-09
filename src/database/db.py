
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


load_dotenv()


# Отримуємо параметри підключення з змінних середовища
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/skillswap"
)


# Створюємо двигун бази даних
engine = create_engine(DATABASE_URL)


# Фабрика сесій для роботи з БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Базовий клас для моделей
Base = declarative_base()


# Dependency для отримання сесії БД
def get_db():
    """
    Створює нову сесію БД для кожного запиту.
    Автоматично закриває її після використання.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

