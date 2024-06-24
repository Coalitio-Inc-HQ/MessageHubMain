from fastapi import FastAPI
from .database.session_database import get_session
from .api.router import router

app= FastAPI()

app.include_router(router)
