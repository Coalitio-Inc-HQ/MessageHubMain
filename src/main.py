from fastapi import FastAPI, Body, APIRouter,Request
from fastapi.responses import RedirectResponse
from .database.session_database import get_session
from .api.messageHub.router import router
from fastapi.middleware.cors import CORSMiddleware
from src.loging.logging_utility import log, LogMessage,log_en
from .settings import settings

from .database.schemes import ChatDTO, MessageDTO,UserDTO

async def lifespan(app: FastAPI):
    log(LogMessage(time=None,heder="Сервер запущен.", heder_dict=None,body=None,level=log_en.INFO))
    yield
    log(LogMessage(time=None,heder="Сервер остановлен.", heder_dict=None,body=None,level=log_en.INFO))

app = FastAPI(lifespan=lifespan)

@app.exception_handler(Exception)
async def exception_handler(request: Request, error: Exception):
    log(LogMessage(time=None,heder="Неизвестная ошибка.", 
                   heder_dict=error.args,body=
                   {"url":str(request.url),"query_params":request.query_params._list,
                    "path_params":request.path_params,
                    },
                    level=log_en.ERROR))
    

print("BACKEND_CORS_ORIGINS:", settings.BACKEND_CORS_ORIGINS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
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
    log(LogMessage(time=None,heder="Webhook add waiting chat", heder_dict=None,body={"id":id,"name":name},level=log_en.INFO))


@router_test.post(settings.END_POINT_SEND_NOTIFICATION_USER_ADDED_TO_CHAT)
async def root(chat: ChatDTO, user: UserDTO):
    log(LogMessage(time=None,heder="Webhook add user to chat", heder_dict=None,body={"user":user,"chat":chat},level=log_en.INFO))


@router_test.post(settings.END_POINT_SEND_NOTIFICATION_DELETED_WAITING_CHAT)
async def root(chat: ChatDTO):
    log(LogMessage(time=None,heder="Webhook deleted waiting chat", heder_dict=None,body={"chat":chat},level=log_en.INFO))


@router_test.post(settings.END_POINT_SEND_MESSAGE)
async def root(message: MessageDTO):
    log(LogMessage(time=None,heder="Webhook sent message", heder_dict=None,body={"message":message},level=log_en.INFO))


@router_test.post(settings.END_POINT_SEND_MESSAGE_BROADCAST)
async def root(message: MessageDTO):
    log(LogMessage(time=None,heder="Webhook sent message broadcast", heder_dict=None,body={"message":message},level=log_en.INFO))

app.include_router(router_test, tags=["webhook"])
