from fastapi import FastAPI, Body, APIRouter
from fastapi.responses import RedirectResponse
from .database.session_database import get_session
from .api.messageHub.router import router
from fastapi.middleware.cors import CORSMiddleware

from .settings import settings

from .database.schemes import ChatDTO, MessageDTO

origins = [
    "http://localhost:8000",
    "http://localhost:8001",
    "http://localhost:8002",
    "http://localhost:8003"
]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# тест хуков
app.include_router(router)

router_test = APIRouter()


@router_test.get("/")
async def root():
    return RedirectResponse("/docs")


@router_test.post(settings.END_POINT_SEND_NOTIFICATION_ADDED_WAITING_CHAT)
async def root(id: int = Body(), name: str = Body()):
    print(f"webhook add waiting chat id:{id} name:{name}")


@router_test.post(settings.END_POINT_SEND_NOTIFICATION_USER_ADDED_TO_CHAT)
async def root(chat: ChatDTO, user_id: int = Body()):
    print(f"webhook add user to chat user_id:{user_id} chat:{chat}")


@router_test.post(settings.END_POINT_SEND_NOTIFICATION_DELETED_WAITING_CHAT)
async def root(chat_id: int = Body()):
    print(f"webhook deleted waiting chat chat_id:{chat_id}")


@router_test.post(settings.END_POINT_SEND_MESSAGE)
async def root(message: MessageDTO):
    print(f"webhook sent message:{message}")


@router_test.post(settings.END_POINT_SEND_MESSAGE_BROADCAST)
async def root(message: MessageDTO):
    print(f"webhook sent message broadcast:{message}")

app.include_router(router_test, tags=["webhook"])
