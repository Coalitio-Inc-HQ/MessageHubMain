from fastapi import APIRouter, Body, Depends, HTTPException, Query
from ....database.session_database import get_session, AsyncSession
from ....database.database_requests import *
from src.loging.logging_utility import log, LogMessage,log_en

from pydantic import BaseModel

router = APIRouter()

from src.database.utilities import insert_data, update_data, select_data_arr, select_data_one_or_none, select_data_one_or_none_quer

from src.auth import verify_api_key

class PlatformIn(BaseModel):
    """
    Модель входных данных для регистрации платформы
    """
    platform_name: str = Field(max_length=30)
    url: str = Field(max_length=256)


@router.post("/platform_registration/{platform_type}")
async def registr_platform(platform_type: str, platform: PlatformIn, session: AsyncSession = Depends(get_session), api_key = Depends(verify_api_key)):
    """
    Регистрирует платформу.
    """

    if len(platform_type) > 3:
        raise HTTPException(status_code=422, detail="len(platform_type)>3")

    db_platform = await select_data_one_or_none(session, PlatformORM, PlatformDTO, PlatformORM.platform_name==platform.platform_name)

    # перезваписываем url если платформа уже существует
    platform_data = platform.model_dump()
    platform_data.update({"platform_type":platform_type})
    if db_platform:
        await update_data(session, PlatformORM, PlatformORM.platform_name==platform.platform_name, **platform_data)
        log(LogMessage(time=None,heder="Обнавлена платформа.", heder_dict={"platform_type":platform_type, "platform": platform},body={"platform":db_platform},level=log_en.INFO))
        return {"status": "ok"}
    else:
        platform_id = await insert_data(session, PlatformORM, platform_data,return_atr=["id"])
        log(LogMessage(time=None,heder="Обнавлена платформа.", heder_dict={"platform_type":platform_type, "platform": platform},body={"platform_id":platform_id},level=log_en.INFO))
        return {"status": "ok"}

@router.post("/get_platforms")
async def get_platforms(session: AsyncSession = Depends(get_session), api_key = Depends(verify_api_key)):
    return await select_data_arr(session, PlatformORM, OutPlatformDTO)