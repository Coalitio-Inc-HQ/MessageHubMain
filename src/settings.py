from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DB_ECHO: bool

    APP_HOST:str
    APP_PORT:int

    DB_HOST_TEST: str
    DB_PORT_TEST: int
    DB_USER_TEST: str
    DB_PASS_TEST: str
    DB_NAME_TEST: str

    END_POINT_SEND_MESSAGE: str
    END_POINT_SEND_MESSAGE_BROADCAST:str
    END_POINT_SEND_NOTIFICATION_ADDED_WAITING_CHAT:str
    END_POINT_SEND_NOTIFICATION_USER_ADDED_TO_CHAT:str
    END_POINT_SEND_NOTIFICATION_DELITED_WAITING_CHAT:str

    @property
    def DATABASE_URL_ASINC(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
