from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
from fastapi.staticfiles import StaticFiles

from src.database.db import engine, get_db
from src.database.models import Base
from src.routes import users, skills, exchanges, reviews, categories, stats
from src.routes.photos import router as photos_router


# Створюємо таблиці (якщо вони не існують)
Base.metadata.create_all(bind=engine)

# Створюємо застосунок
app = FastAPI(
    title="SkillSwap API",
    description="REST API для платформи обміну навичками",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Налаштування CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["<http://localhost:3000>"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Підключаємо маршрути
app.include_router(users.router, prefix="/api")
app.include_router(skills.router, prefix="/api")
app.include_router(exchanges.router, prefix="/api")
app.include_router(reviews.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(photos_router, prefix="/api")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def read_root():
    return {
        "message": "Ласкаво просимо до SkillSwap API v2.0",
        "documentation": "/docs",
        "endpoints": {
            "users": "/api/users",
            "skills": "/api/skills",
            "exchanges": "/api/exchanges",
            "reviews": "/api/reviews"
        }
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Перевірка стану застосунку та БД."""
    try:
# Простий запит для перевірки з'єднання з БД
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "database": db_status,
        "version": "2.0.0"
    }

@app.on_event("startup")
async def startup_event():
    """Дії при запуску застосунку."""
    print("🚀 SkillSwap API запущено!")
    print("📚 Документація доступна на: <http://localhost:8000/docs>")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
