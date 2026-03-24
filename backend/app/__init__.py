import asyncio
from app.database import engine, Base
from app import models

async def init_db():
    async with engine.begin() as conn:
        # Создаём все таблицы в схеме constructor
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully")

if __name__ == "__main__":
    asyncio.run(init_db())