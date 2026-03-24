import asyncio
from app.database import engine, Base
from app import models
from sqlalchemy import text

async def init_db():
    async with engine.begin() as conn:
        # Создаём таблицы
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created")

        # Вставляем типы полей, если их нет
        types = [
    ('string', 'Строка'),
    ('text', 'Длинный текст'),
    ('number', 'Число'),
    ('date', 'Дата'),
    ('datetime', 'Дата и время'),
    ('period', 'Период'),
    ('radio', 'Radio-кнопка'),
    ('checkbox', 'Флажок (Да/Нет)'),
    ('select', 'Выпадающий список (один)'),
    ('multiselect', 'Выпадающий список (множественный)'),
    ('coordinates', 'Координаты (широта, долгота)')
]
        for code, name in types:
            await conn.execute(
                text("INSERT INTO constructor.field_types (code, name) VALUES (:code, :name) ON CONFLICT (code) DO NOTHING"),
                {"code": code, "name": name}
            )
        await conn.commit()
        print("Field types inserted")

if __name__ == "__main__":
    asyncio.run(init_db())