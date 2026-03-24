from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Убираем options из URL, используем connect_args для установки search_path
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    connect_args={"server_settings": {"search_path": "constructor"}}
)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session