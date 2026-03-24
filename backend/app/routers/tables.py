from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/tables", tags=["tables"])

@router.post("", response_model=schemas.Table, status_code=status.HTTP_201_CREATED)
async def create_table(
    table: schemas.TableCreate,
    db: AsyncSession = Depends(get_db)
):
    # Проверка формы
    form = await crud.get_form(db, table.formId)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    # Проверка полей
    for fid in table.columns:
        if not await crud.get_field(db, fid):
            raise HTTPException(status_code=400, detail=f"Field with id {fid} does not exist")
    db_table = await crud.create_table(db, table)
    if not db_table:
        raise HTTPException(status_code=400, detail="Table could not be created")
    return db_table

@router.get("", response_model=List[schemas.Table])
async def read_tables(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_tables(db, skip, limit)

@router.get("/{table_id}", response_model=schemas.Table)
async def read_table(
    table_id: int,
    db: AsyncSession = Depends(get_db)
):
    db_table = await crud.get_table(db, table_id)
    if not db_table:
        raise HTTPException(status_code=404, detail="Table not found")
    return db_table

@router.put("/{table_id}", response_model=schemas.Table)
async def update_table(
    table_id: int,
    table_update: schemas.TableUpdate,
    db: AsyncSession = Depends(get_db)
):
    if table_update.columns is not None:
        for fid in table_update.columns:
            if not await crud.get_field(db, fid):
                raise HTTPException(status_code=400, detail=f"Field with id {fid} does not exist")
    db_table = await crud.update_table(db, table_id, table_update)
    if not db_table:
        raise HTTPException(status_code=404, detail="Table not found")
    return db_table

@router.delete("/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_table(
    table_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await crud.delete_table(db, table_id)
    if not success:
        raise HTTPException(status_code=404, detail="Table not found")
    return