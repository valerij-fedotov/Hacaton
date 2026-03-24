from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/forms", tags=["forms"])

@router.post("", response_model=schemas.Form, status_code=status.HTTP_201_CREATED)
async def create_form(form: schemas.FormCreate, db: AsyncSession = Depends(get_db)):
    # Проверка, что все field_ids существуют
    for fid in form.field_ids:
        if not await crud.get_field(db, fid):
            raise HTTPException(status_code=400, detail=f"Field with id {fid} does not exist")
    return await crud.create_form(db, form)

@router.get("", response_model=List[schemas.Form])
async def read_forms(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_forms(db, skip, limit)

@router.get("/{form_id}", response_model=schemas.Form)
async def read_form(form_id: int, db: AsyncSession = Depends(get_db)):
    db_form = await crud.get_form(db, form_id)
    if not db_form:
        raise HTTPException(status_code=404, detail="Form not found")
    return db_form

@router.put("/{form_id}", response_model=schemas.Form)
async def update_form(form_id: int, form_update: schemas.FormUpdate, db: AsyncSession = Depends(get_db)):
    if form_update.field_ids:
        for fid in form_update.field_ids:
            if not await crud.get_field(db, fid):
                raise HTTPException(status_code=400, detail=f"Field with id {fid} does not exist")
    db_form = await crud.update_form(db, form_id, form_update)
    if not db_form:
        raise HTTPException(status_code=404, detail="Form not found")
    return db_form

@router.delete("/{form_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_form(form_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud.delete_form(db, form_id)
    if not success:
        raise HTTPException(status_code=404, detail="Form not found")
    return