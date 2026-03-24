from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/records", tags=["records"])

@router.post("", response_model=schemas.Record, status_code=status.HTTP_201_CREATED)
async def create_record(record: schemas.RecordCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем форму
    form = await crud.get_form(db, record.form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    # Здесь можно добавить валидацию данных по полям формы
    return await crud.create_record(db, record)

@router.get("", response_model=List[schemas.Record])
async def read_records(
    form_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    items, total = await crud.get_records(db, form_id, skip, limit)
    # Для пагинации можно вернуть объект с total, но фронтенд ожидает просто массив
    # Пока возвращаем массив, добавим total в заголовки, если нужно
    return items

@router.get("/{record_id}", response_model=schemas.Record)
async def read_record(record_id: int, db: AsyncSession = Depends(get_db)):
    record = await crud.get_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@router.put("/{record_id}", response_model=schemas.Record)
async def update_record(record_id: int, record_update: schemas.RecordUpdate, db: AsyncSession = Depends(get_db)):
    updated = await crud.update_record(db, record_id, record_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Record not found")
    return updated

@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_record(record_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud.delete_record(db, record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Record not found")
    return