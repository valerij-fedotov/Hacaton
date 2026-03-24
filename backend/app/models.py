from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON, Text, DateTime, func, BigInteger, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class FieldType(Base):
    __tablename__ = "field_types"
    __table_args__ = {"schema": "constructor"}

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Field(Base):
    __tablename__ = "fields"
    __table_args__ = {"schema": "constructor"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    key = Column(String(100), nullable=False, unique=True)
    type_id = Column(Integer, ForeignKey("constructor.field_types.id", ondelete="RESTRICT"), nullable=False)
    config = Column(JSONB, nullable=False, server_default='{}')
    is_system = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    field_type = relationship("FieldType")
    form_fields = relationship("FormField", back_populates="field", cascade="all, delete-orphan")
    table_columns = relationship("TableColumn", back_populates="field", cascade="all, delete-orphan")

class Form(Base):
    __tablename__ = "forms"
    __table_args__ = {"schema": "constructor"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    fields = relationship("FormField", back_populates="form", cascade="all, delete-orphan")
    tables = relationship("Table", back_populates="form", cascade="all, delete-orphan")
    records = relationship("Record", back_populates="form", cascade="all, delete-orphan")

class FormField(Base):
    __tablename__ = "form_fields"
    __table_args__ = (
        UniqueConstraint("form_id", "field_id", name="uq_form_field"),
        {"schema": "constructor"}
    )

    id = Column(Integer, primary_key=True)
    form_id = Column(Integer, ForeignKey("constructor.forms.id", ondelete="CASCADE"), nullable=False)
    field_id = Column(Integer, ForeignKey("constructor.fields.id", ondelete="RESTRICT"), nullable=False)
    sort_order = Column(Integer, default=0)
    is_required = Column(Boolean, default=False)
    display_name = Column(String(200))
    width = Column(String(20), default='full')
    validation_rules = Column(JSONB, default={})
    depends_on = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    form = relationship("Form", back_populates="fields")
    field = relationship("Field", back_populates="form_fields")

class Table(Base):
    __tablename__ = "tables"
    __table_args__ = {"schema": "constructor"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    form_id = Column(Integer, ForeignKey("constructor.forms.id", ondelete="CASCADE"), nullable=False)
    config = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    form = relationship("Form", back_populates="tables")
    columns = relationship("TableColumn", back_populates="table", cascade="all, delete-orphan")

class TableColumn(Base):
    __tablename__ = "table_columns"
    __table_args__ = {"schema": "constructor"}

    id = Column(Integer, primary_key=True)
    table_id = Column(Integer, ForeignKey("constructor.tables.id", ondelete="CASCADE"), nullable=False)
    field_id = Column(Integer, ForeignKey("constructor.fields.id", ondelete="RESTRICT"), nullable=False)
    sort_order = Column(Integer, default=0)
    display_name = Column(String(200))
    width = Column(Integer)
    format_config = Column(JSONB, default={})
    is_visible = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    table = relationship("Table", back_populates="columns")
    field = relationship("Field", back_populates="table_columns")

class Record(Base):
    __tablename__ = "records"
    __table_args__ = {"schema": "constructor"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_id = Column(Integer, ForeignKey("constructor.forms.id", ondelete="CASCADE"), nullable=False)
    data = Column(JSONB, nullable=False)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    form = relationship("Form", back_populates="records")

class AuditLog(Base):
    __tablename__ = "audit_log"
    __table_args__ = {"schema": "constructor"}

    id = Column(BigInteger, primary_key=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(50), nullable=False)
    action = Column(String(20), nullable=False)
    old_data = Column(JSONB)
    new_data = Column(JSONB)
    user_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "constructor"}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(200), nullable=False, unique=True)
    password_hash = Column(String(255))
    role = Column(String(50), default='user')
    created_at = Column(DateTime(timezone=True), server_default=func.now())