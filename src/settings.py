from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DB_ECHO: bool

    APP_HOST: str
    APP_PORT: int

    DB_HOST_TEST: str
    DB_PORT_TEST: int
    DB_USER_TEST: str
    DB_PASS_TEST: str
    DB_NAME_TEST: str

    END_POINT_SEND_MESSAGE: str
    END_POINT_SEND_NOTIFICATION_ADDED_CHAT:str
    END_POINT_SEND_NOTIFICATION_USER_ADDED_TO_CHAT: str


    BACKEND_CORS_ORIGINS: str

    LOG_PATH:str

    @property
    def DATABASE_URL_ASINC(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def BACKEND_CORS_ORIGINS(self):
        return self.BACKEND_CORS_ORIGINS.split(",")

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
