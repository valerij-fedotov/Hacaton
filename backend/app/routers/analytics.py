from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/")
async def get_analytics(db: AsyncSession = Depends(get_db)):
    # Заглушка для будущей аналитики
    return {"message": "Analytics not implemented yet"}