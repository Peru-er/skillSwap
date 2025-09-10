
import os
from uuid import uuid4
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from fastapi import Depends
from typing import List, Dict
from pydantic import BaseModel

# Шлях для збереження файлів (створи цю папку у проєкті)
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(
    prefix="/photos",
    tags=["Photos"]
)

MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
ALLOWED = {"image/jpeg": ".jpg", "image/png": ".png"}

class PhotoOut(BaseModel):
    filename: str
    url: str
    uploaded_at: datetime

# Простий in-memory список (вказано в підказці).
# Якщо сервер перезапустити — список пропаде. Для персистентності треба БД.
_photos: List[Dict] = []

@router.post("/upload", response_model=PhotoOut, status_code=status.HTTP_201_CREATED)
async def upload_photo(file: UploadFile = File(...)):
    # Валідація content-type
    if file.content_type not in ALLOWED:
        raise HTTPException(status_code=400, detail="Only JPEG and PNG allowed")

    # Читаємо розмір файлу — без повного збереження у пам'ять
    contents = await file.read()
    size = len(contents)
    if size > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File too large. Max 5MB")

    ext = ALLOWED[file.content_type]
    unique_name = f"{uuid4().hex}{ext}"
    dest_path = os.path.join(UPLOAD_DIR, unique_name)

    # Запис на диск
    with open(dest_path, "wb") as f:
        f.write(contents)

    # Створюємо URL — припустимо, що статичні файли будуть доступні під /uploads/
    url = f"/uploads/{unique_name}"
    entry = {
        "filename": unique_name,
        "url": url,
        "uploaded_at": datetime.utcnow()
    }
    # додаємо в початок щоб сортування вже було (новіші першими)
    _photos.insert(0, entry)

    return entry

@router.get("/list", response_model=List[PhotoOut])
def list_photos():
    return _photos

@router.get("/{filename}")
def get_photo(filename: str):
    path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Photo not found")
    # Повертаємо файл для перегляду
    return FileResponse(path, media_type="application/octet-stream")

