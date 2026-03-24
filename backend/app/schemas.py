from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Dict

# ---------- Поля ----------
class FieldBase(BaseModel):
    name: str
    key: str
    type: str
    options: Dict[str, Any] = {}

class FieldCreate(FieldBase):
    pass

class FieldUpdate(BaseModel):
    name: Optional[str] = None
    key: Optional[str] = None
    type: Optional[str] = None
    options: Optional[Dict[str, Any]] = None

class Field(FieldBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ---------- Формы ----------
class FormBase(BaseModel):
    name: str
    field_ids: List[int]   # порядок полей

class FormCreate(FormBase):
    pass

class FormUpdate(BaseModel):
    name: Optional[str] = None
    field_ids: Optional[List[int]] = None

class Form(FormBase):
    id: int
    created_at: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

# ---------- Таблицы ----------
class TableBase(BaseModel):
    name: str
    form_id: int
    columns: List[int]   # ID полей для отображения

class TableCreate(TableBase):
    pass

class Table(TableBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ---------- Записи ----------
class RecordBase(BaseModel):
    form_id: int
    data: Dict[str, Any]

class RecordCreate(RecordBase):
    pass

class RecordUpdate(BaseModel):
    data: Dict[str, Any]

class Record(RecordBase):
    id: int
    created_at: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)