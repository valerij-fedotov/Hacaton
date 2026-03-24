from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/fields", tags=["fields"])

@router.get("", response_model=List[schemas.Field])
async def read_fields(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_fields(db, skip, limit)

@router.post("", response_model=schemas.Field, status_code=status.HTTP_201_CREATED)
async def create_field(field: schemas.FieldCreate, db: AsyncSession = Depends(get_db)):
    existing = await crud.get_field_by_key(db, field.key)
    if existing:
        raise HTTPException(status_code=400, detail="Field with this key already exists")
    return await crud.create_field(db, field)

@router.get("/{field_id}", response_model=schemas.Field)
async def read_field(field_id: int, db: AsyncSession = Depends(get_db)):
    db_field = await crud.get_field(db, field_id)
    if not db_field:
        raise HTTPException(status_code=404, detail="Field not found")
    return db_field

@router.put("/{field_id}", response_model=schemas.Field)
async def update_field(field_id: int, field_update: schemas.FieldUpdate, db: AsyncSession = Depends(get_db)):
    db_field = await crud.update_field(db, field_id, field_update)
    if not db_field:
        raise HTTPException(status_code=404, detail="Field not found")
    return db_field

@router.delete("/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_field(field_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud.delete_field(db, field_id)
    if not success:
        raise HTTPException(status_code=404, detail="Field not found")
    return