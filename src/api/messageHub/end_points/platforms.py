from fastapi import APIRouter, Body, Depends, HTTPException, Query
from ....database.session_database import get_session, AsyncSession
from ....database.database_requests import *
from src.loging.logging_utility import log, LogMessage,log_en

from pydantic import BaseModel

router = APIRouter()


class PlatformIn(BaseModel):
    """
    Модель входных данных для регистрации платформы
    """
    platform_name: str = Field(max_length=30)
    url: str = Field(max_length=256)


@router.post("/platform_registration/{platform_type}")
async def registr_platform(platform_type: str, platform: PlatformIn, session: AsyncSession = Depends(get_session)):
    """
    Регистрирует платформу бота.
    """
    if len(platform_type) > 3:
        raise HTTPException(status_code=422, detail="len(platform_type)>3")
    platforms = await get_platforms_by_name(session=session, platform_name=platform.platform_name)
    
    # перезваписываем url если платформа уже существует
    if not len(platforms) == 0:
        await update_platforms_by_name(session=session, platform_name=platform.platform_name, url=platform.url)
        log(LogMessage(time=None,heder="Обнавлена платформа.", heder_dict=None,body={"platform":platforms[0]},level=log_en.INFO))
        return {"status": "ok"}
    else:
        plat = await platform_registration(session=session, platform_type=platform_type, platform_name=platform.platform_name, url=platform.url)
        log(LogMessage(time=None,heder="Обнавлена платформа.", heder_dict=None,body={"platform":plat},level=log_en.INFO))
        return {"status": "ok"}
