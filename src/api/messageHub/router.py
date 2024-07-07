from fastapi import APIRouter, Body, Depends, HTTPException
from ...database.session_database import get_session, AsyncSession
from ...database.database_requests import *
from httpx import AsyncClient
from typing import Union

from ...settings import settings

from .end_points.platforms import router as platform_router
from .end_points.user_registration import router as user_registration_router
from .end_points.chats import router as chat_router
from .end_points.messages import router as message_router

router = APIRouter(prefix="/message_service")

router.include_router(platform_router)
router.include_router(user_registration_router)
router.include_router(chat_router)
router.include_router(message_router)