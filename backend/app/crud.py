from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Tuple

from app import models, schemas

# ---------- Fields ----------
async def get_fields(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Field).offset(skip).limit(limit))
    return result.scalars().all()

async def get_field(db: AsyncSession, field_id: int):
    result = await db.execute(select(models.Field).where(models.Field.id == field_id))
    return result.scalar_one_or_none()

async def get_field_by_key(db: AsyncSession, key: str):
    result = await db.execute(select(models.Field).where(models.Field.key == key))
    return result.scalar_one_or_none()

async def create_field(db: AsyncSession, field: schemas.FieldCreate):
    db_field = models.Field(**field.model_dump())
    db.add(db_field)
    await db.commit()
    await db.refresh(db_field)
    return db_field

async def update_field(db: AsyncSession, field_id: int, field_update: schemas.FieldUpdate):
    db_field = await get_field(db, field_id)
    if not db_field:
        return None
    update_data = field_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_field, key, value)
    await db.commit()
    await db.refresh(db_field)
    return db_field

async def delete_field(db: AsyncSession, field_id: int):
    db_field = await get_field(db, field_id)
    if not db_field:
        return False
    # Проверка использования в формах
    forms_using = await db.execute(
        select(models.Form).where(models.Form.field_ids.contains([field_id]))
    )
    if forms_using.scalar_one_or_none():
        # Можно вернуть ошибку, но для простоты удалим из всех форм
        # (можно реализовать каскадное удаление из форм и таблиц)
        pass
    await db.delete(db_field)
    await db.commit()
    return True

# ---------- Forms ----------
async def get_forms(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Form).offset(skip).limit(limit))
    return result.scalars().all()

async def get_form(db: AsyncSession, form_id: int):
    result = await db.execute(select(models.Form).where(models.Form.id == form_id))
    return result.scalar_one_or_none()

async def create_form(db: AsyncSession, form: schemas.FormCreate):
    db_form = models.Form(name=form.name, field_ids=form.field_ids)
    db.add(db_form)
    await db.commit()
    await db.refresh(db_form)
    return db_form

async def update_form(db: AsyncSession, form_id: int, form_update: schemas.FormUpdate):
    db_form = await get_form(db, form_id)
    if not db_form:
        return None
    update_data = form_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_form, key, value)
    await db.commit()
    await db.refresh(db_form)
    return db_form

async def delete_form(db: AsyncSession, form_id: int):
    db_form = await get_form(db, form_id)
    if not db_form:
        return False
    await db.delete(db_form)   # каскадно удалит records и tables (cascade)
    await db.commit()
    return True

# ---------- Tables ----------
async def get_tables(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Table).offset(skip).limit(limit))
    return result.scalars().all()

async def get_table(db: AsyncSession, table_id: int):
    result = await db.execute(select(models.Table).where(models.Table.id == table_id))
    return result.scalar_one_or_none()

async def create_table(db: AsyncSession, table: schemas.TableCreate):
    # Проверяем существование формы
    form = await get_form(db, table.form_id)
    if not form:
        return None
    db_table = models.Table(**table.model_dump())
    db.add(db_table)
    await db.commit()
    await db.refresh(db_table)
    return db_table

async def delete_table(db: AsyncSession, table_id: int):
    db_table = await get_table(db, table_id)
    if not db_table:
        return False
    await db.delete(db_table)
    await db.commit()
    return True

# ---------- Records ----------
async def get_records(db: AsyncSession, form_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    query = select(models.Record)
    if form_id is not None:
        query = query.where(models.Record.form_id == form_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()
    # Общее количество
    count_query = select(models.Record).where(models.Record.form_id == form_id) if form_id else select(models.Record)
    total = await db.execute(select(func.count()).select_from(count_query.subquery()))
    total = total.scalar_one()
    return items, total

async def get_record(db: AsyncSession, record_id: int):
    result = await db.execute(select(models.Record).where(models.Record.id == record_id))
    return result.scalar_one_or_none()

async def create_record(db: AsyncSession, record: schemas.RecordCreate):
    # Проверяем форму
    form = await get_form(db, record.form_id)
    if not form:
        return None
    db_record = models.Record(**record.model_dump())
    db.add(db_record)
    await db.commit()
    await db.refresh(db_record)
    return db_record

async def update_record(db: AsyncSession, record_id: int, record_update: schemas.RecordUpdate):
    db_record = await get_record(db, record_id)
    if not db_record:
        return None
    db_record.data = record_update.data
    await db.commit()
    await db.refresh(db_record)
    return db_record

async def delete_record(db: AsyncSession, record_id: int):
    db_record = await get_record(db, record_id)
    if not db_record:
        return False
    await db.delete(db_record)
    await db.commit()
    return True