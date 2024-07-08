import uvicorn
from src.main import app
from src.settings import settings

uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)
