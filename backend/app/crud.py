from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional, Tuple, Dict, Any
from app import models, schemas
from sqlalchemy.exc import IntegrityError

# -------- Field types ----------
async def get_field_type_by_code(db: AsyncSession, code: str) -> Optional[models.FieldType]:
    result = await db.execute(select(models.FieldType).where(models.FieldType.code == code))
    return result.scalar_one_or_none()

# -------- Fields ----------
async def get_fields(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[schemas.Field]:
    result = await db.execute(
        select(models.Field)
        .offset(skip)
        .limit(limit)
        .options(selectinload(models.Field.field_type))
    )
    db_fields = result.scalars().all()
    out = []
    for f in db_fields:
        out.append(schemas.Field(
            id=f.id,
            name=f.name,
            key=f.key,
            type=f.field_type.code if f.field_type else 'text',
            options=f.config or {},
            created_at=f.created_at,
            updated_at=f.updated_at
        ))
    return out

async def get_field(db: AsyncSession, field_id: int) -> Optional[schemas.Field]:
    result = await db.execute(
        select(models.Field)
        .where(models.Field.id == field_id)
        .options(selectinload(models.Field.field_type))
    )
    f = result.scalar_one_or_none()
    if not f:
        return None
    return schemas.Field(
        id=f.id,
        name=f.name,
        key=f.key,
        type=f.field_type.code if f.field_type else 'text',
        options=f.config or {},
        created_at=f.created_at,
        updated_at=f.updated_at
    )

async def get_field_by_key(db: AsyncSession, key: str) -> Optional[schemas.Field]:
    result = await db.execute(
        select(models.Field)
        .where(models.Field.key == key)
        .options(selectinload(models.Field.field_type))
    )
    f = result.scalar_one_or_none()
    if not f:
        return None
    return schemas.Field(
        id=f.id,
        name=f.name,
        key=f.key,
        type=f.field_type.code if f.field_type else 'text',
        options=f.config or {},
        created_at=f.created_at,
        updated_at=f.updated_at
    )

async def create_field(db: AsyncSession, field: schemas.FieldCreate) -> schemas.Field:
    ft = await get_field_type_by_code(db, field.type)
    if not ft:
        raise ValueError(f"Unknown field type: {field.type}")
    db_field = models.Field(
        name=field.name,
        key=field.key,
        type_id=ft.id,
        config=field.options or {},
        is_system=False
    )
    db.add(db_field)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ValueError("Field with this key already exists")
    await db.refresh(db_field)
    return schemas.Field(
        id=db_field.id,
        name=db_field.name,
        key=db_field.key,
        type=ft.code,
        options=db_field.config or {},
        created_at=db_field.created_at,
        updated_at=db_field.updated_at
    )

async def update_field(db: AsyncSession, field_id: int, field_update: schemas.FieldUpdate) -> Optional[schemas.Field]:
    db_field = await db.get(models.Field, field_id)
    if not db_field:
        return None
    if field_update.name is not None:
        db_field.name = field_update.name
    if field_update.key is not None:
        db_field.key = field_update.key
    if field_update.type is not None:
        ft = await get_field_type_by_code(db, field_update.type)
        if not ft:
            raise ValueError(f"Unknown field type: {field_update.type}")
        db_field.type_id = ft.id
    if field_update.options is not None:
        db_field.config = field_update.options
    await db.commit()
    await db.refresh(db_field)
    ft = await db.get(models.FieldType, db_field.type_id)
    return schemas.Field(
        id=db_field.id,
        name=db_field.name,
        key=db_field.key,
        type=ft.code if ft else 'text',
        options=db_field.config or {},
        created_at=db_field.created_at,
        updated_at=db_field.updated_at
    )

async def delete_field(db: AsyncSession, field_id: int) -> bool:
    db_field = await db.get(models.Field, field_id)
    if not db_field:
        return False
    await db.delete(db_field)
    await db.commit()
    return True

# -------- Forms ----------
# -------- Forms ----------
async def get_forms(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[schemas.Form]:
    result = await db.execute(
        select(models.Form)
        .offset(skip)
        .limit(limit)
        .options(selectinload(models.Form.fields))
    )
    forms = result.scalars().all()
    out = []
    for form in forms:
        field_ids = [ff.field_id for ff in sorted(form.fields, key=lambda x: x.sort_order)]
        out.append(schemas.Form(
            id=form.id,
            name=form.name,
            field_ids=field_ids,
            created_at=form.created_at,
            updated_at=form.updated_at
        ))
    return out

async def get_form(db: AsyncSession, form_id: int) -> Optional[schemas.Form]:
    result = await db.execute(
        select(models.Form)
        .where(models.Form.id == form_id)
        .options(selectinload(models.Form.fields))
    )
    form = result.scalar_one_or_none()
    if not form:
        return None
    field_ids = [ff.field_id for ff in sorted(form.fields, key=lambda x: x.sort_order)]
    return schemas.Form(
        id=form.id,
        name=form.name,
        field_ids=field_ids,
        created_at=form.created_at,
        updated_at=form.updated_at
    )

async def create_form(db: AsyncSession, form: schemas.FormCreate) -> schemas.Form:
    db_form = models.Form(name=form.name)
    db.add(db_form)
    await db.flush()
    for idx, fid in enumerate(form.field_ids):
        ff = models.FormField(
            form_id=db_form.id,
            field_id=fid,
            sort_order=idx,
            is_required=False,
            width='full'
        )
        db.add(ff)
    await db.commit()
    await db.refresh(db_form)
    return schemas.Form(
        id=db_form.id,
        name=db_form.name,
        field_ids=form.field_ids,
        created_at=db_form.created_at,
        updated_at=db_form.updated_at
    )

async def update_form(db: AsyncSession, form_id: int, form_update: schemas.FormUpdate) -> Optional[schemas.Form]:
    db_form = await db.get(models.Form, form_id)
    if not db_form:
        return None
    if form_update.name is not None:
        db_form.name = form_update.name
    if form_update.field_ids is not None:
        await db.execute(delete(models.FormField).where(models.FormField.form_id == form_id))
        for idx, fid in enumerate(form_update.field_ids):
            ff = models.FormField(
                form_id=db_form.id,
                field_id=fid,
                sort_order=idx,
                is_required=False,
                width='full'
            )
            db.add(ff)
    await db.commit()
    await db.refresh(db_form)
    result = await db.execute(
        select(models.FormField.field_id)
        .where(models.FormField.form_id == form_id)
        .order_by(models.FormField.sort_order)
    )
    field_ids = [row[0] for row in result.all()]
    return schemas.Form(
        id=db_form.id,
        name=db_form.name,
        field_ids=field_ids,
        created_at=db_form.created_at,
        updated_at=db_form.updated_at
    )
    db_form = await db.get(models.Form, form_id)
    if not db_form:
        return None
    if form_update.name is not None:
        db_form.name = form_update.name
    if form_update.fieldIds is not None:
        await db.execute(delete(models.FormField).where(models.FormField.form_id == form_id))
        for idx, fid in enumerate(form_update.fieldIds):
            ff = models.FormField(
                form_id=db_form.id,
                field_id=fid,
                sort_order=idx,
                is_required=False,
                width='full'
            )
            db.add(ff)
    await db.commit()
    await db.refresh(db_form)
    result = await db.execute(
        select(models.FormField.field_id)
        .where(models.FormField.form_id == form_id)
        .order_by(models.FormField.sort_order)
    )
    field_ids = [row[0] for row in result.all()]
    return schemas.Form(
        id=db_form.id,
        name=db_form.name,
        fieldIds=field_ids,
        created_at=db_form.created_at,
        updated_at=db_form.updated_at
    )

async def delete_form(db: AsyncSession, form_id: int) -> bool:
    db_form = await db.get(models.Form, form_id)
    if not db_form:
        return False
    await db.delete(db_form)
    await db.commit()
    return True

# -------- Tables ----------
async def get_tables(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[schemas.Table]:
    result = await db.execute(
        select(models.Table)
        .offset(skip)
        .limit(limit)
        .options(selectinload(models.Table.columns))
    )
    tables = result.scalars().all()
    out = []
    for t in tables:
        columns = [tc.field_id for tc in sorted(t.columns, key=lambda x: x.sort_order)]
        out.append(schemas.Table(
            id=t.id,
            name=t.name,
            formId=t.form_id,
            columns=columns,
            created_at=t.created_at,
            updated_at=t.updated_at
        ))
    return out

async def get_table(db: AsyncSession, table_id: int) -> Optional[schemas.Table]:
    result = await db.execute(
        select(models.Table)
        .where(models.Table.id == table_id)
        .options(selectinload(models.Table.columns))
    )
    t = result.scalar_one_or_none()
    if not t:
        return None
    columns = [tc.field_id for tc in sorted(t.columns, key=lambda x: x.sort_order)]
    return schemas.Table(
        id=t.id,
        name=t.name,
        formId=t.form_id,
        columns=columns,
        created_at=t.created_at,
        updated_at=t.updated_at
    )

async def create_table(db: AsyncSession, table: schemas.TableCreate) -> Optional[schemas.Table]:
    form = await db.get(models.Form, table.formId)
    if not form:
        return None
    db_table = models.Table(name=table.name, form_id=table.formId)
    db.add(db_table)
    await db.flush()
    for idx, fid in enumerate(table.columns):
        tc = models.TableColumn(
            table_id=db_table.id,
            field_id=fid,
            sort_order=idx,
            is_visible=True
        )
        db.add(tc)
    await db.commit()
    await db.refresh(db_table)
    return schemas.Table(
        id=db_table.id,
        name=db_table.name,
        formId=db_table.form_id,
        columns=table.columns,
        created_at=db_table.created_at,
        updated_at=db_table.updated_at
    )

async def update_table(db: AsyncSession, table_id: int, table_update: schemas.TableUpdate) -> Optional[schemas.Table]:
    db_table = await db.get(models.Table, table_id)
    if not db_table:
        return None
    if table_update.name is not None:
        db_table.name = table_update.name
    if table_update.formId is not None:
        form = await db.get(models.Form, table_update.formId)
        if not form:
            return None
        db_table.form_id = table_update.formId
    if table_update.columns is not None:
        await db.execute(delete(models.TableColumn).where(models.TableColumn.table_id == table_id))
        for idx, fid in enumerate(table_update.columns):
            tc = models.TableColumn(
                table_id=db_table.id,
                field_id=fid,
                sort_order=idx,
                is_visible=True
            )
            db.add(tc)
    await db.commit()
    await db.refresh(db_table)
    result = await db.execute(
        select(models.TableColumn.field_id)
        .where(models.TableColumn.table_id == table_id)
        .order_by(models.TableColumn.sort_order)
    )
    columns = [row[0] for row in result.all()]
    return schemas.Table(
        id=db_table.id,
        name=db_table.name,
        formId=db_table.form_id,
        columns=columns,
        created_at=db_table.created_at,
        updated_at=db_table.updated_at
    )

async def delete_table(db: AsyncSession, table_id: int) -> bool:
    db_table = await db.get(models.Table, table_id)
    if not db_table:
        return False
    await db.delete(db_table)
    await db.commit()
    return True

# -------- Records ----------
async def get_records(
    db: AsyncSession,
    form_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[models.Record], int]:
    query = select(models.Record)
    if form_id is not None:
        query = query.where(models.Record.form_id == form_id)
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.execute(count_query)
    total = total.scalar_one()
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()
    return items, total

async def get_record(db: AsyncSession, record_id: int) -> Optional[models.Record]:
    result = await db.execute(select(models.Record).where(models.Record.id == record_id))
    return result.scalar_one_or_none()

async def create_record(db: AsyncSession, record: schemas.RecordCreate, user_id: Optional[int] = None) -> Optional[models.Record]:
    form = await db.get(models.Form, record.form_id)
    if not form:
        return None
    db_record = models.Record(
        form_id=record.form_id,
        data=record.data,
        created_by=user_id,
        updated_by=user_id
    )
    db.add(db_record)
    await db.commit()
    await db.refresh(db_record)
    return db_record

async def update_record(db: AsyncSession, record_id: int, record_update: schemas.RecordUpdate, user_id: Optional[int] = None) -> Optional[models.Record]:
    db_record = await get_record(db, record_id)
    if not db_record:
        return None
    db_record.data = record_update.data
    db_record.updated_by = user_id
    await db.commit()
    await db.refresh(db_record)
    return db_record

async def delete_record(db: AsyncSession, record_id: int) -> bool:
    db_record = await get_record(db, record_id)
    if not db_record:
        return False
    await db.delete(db_record)
    await db.commit()
    return True