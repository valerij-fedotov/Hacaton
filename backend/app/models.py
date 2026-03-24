from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Field(Base):
    __tablename__ = "fields"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)      # отображаемое имя
    key = Column(String(255), nullable=False, unique=True)  # технический ключ
    type = Column(String(50), nullable=False)       # тип поля (string, text, number...)
    options = Column(JSON, nullable=False, server_default='{}')  # доп. настройки

class Form(Base):
    __tablename__ = "forms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    field_ids = Column(JSON, nullable=False)        # список ID полей (порядок важен)
    created_at = Column(Text, server_default=func.now())  # можно использовать DateTime, но для простоты Text

    # Связи (опционально, для удобства)
    records = relationship("Record", back_populates="form", cascade="all, delete-orphan")
    tables = relationship("Table", back_populates="form", cascade="all, delete-orphan")

class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    form_id = Column(Integer, ForeignKey("forms.id", ondelete="CASCADE"), nullable=False)
    columns = Column(JSON, nullable=False)          # список ID полей, отображаемых в таблице

    form = relationship("Form", back_populates="tables")

class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("forms.id", ondelete="CASCADE"), nullable=False)
    data = Column(JSON, nullable=False)             # значения полей по ключам (key: value)
    created_at = Column(Text, server_default=func.now())

    form = relationship("Form", back_populates="records")