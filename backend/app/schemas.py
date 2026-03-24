from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from uuid import UUID

# ---------- Field Types ----------
class FieldTypeBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None

class FieldType(FieldTypeBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

# ---------- Fields ----------
class FieldBase(BaseModel):
    name: str
    key: str
    type: str                      # фронт шлёт type как строку
    options: Dict[str, Any] = {}   # фронт шлёт options

class FieldCreate(FieldBase):
    pass

class FieldUpdate(BaseModel):
    name: Optional[str] = None
    key: Optional[str] = None
    type: Optional[str] = None
    options: Optional[Dict[str, Any]] = None

class Field(FieldBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

# ---------- Forms ----------
class FormBase(BaseModel):
    name: str
    field_ids: List[int]   # фронт шлёт field_ids (snake_case)

class FormCreate(FormBase):
    pass

class FormUpdate(BaseModel):
    name: Optional[str] = None
    field_ids: Optional[List[int]] = None

class Form(FormBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

# ---------- Tables ----------
class TableBase(BaseModel):
    name: str
    formId: int          # фронт шлёт formId (camelCase)
    columns: List[int]

class TableCreate(TableBase):
    pass

class TableUpdate(BaseModel):
    name: Optional[str] = None
    formId: Optional[int] = None
    columns: Optional[List[int]] = None

class Table(TableBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

# ---------- Records ----------
class RecordBase(BaseModel):
    form_id: int
    data: Dict[str, Any]

class RecordCreate(RecordBase):
    pass

class RecordUpdate(BaseModel):
    data: Dict[str, Any]

class Record(RecordBase):
    id: UUID
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

# ---------- Users ----------
class UserBase(BaseModel):
    username: str
    email: str
    role: str = 'user'

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)