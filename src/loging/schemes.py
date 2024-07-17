from pydantic import BaseModel
from enum import Enum
from typing import Any

class log_en (Enum):
    INFO = "info"
    ERROR = "error"


class LogMessage (BaseModel):
    time: str | None
    level: log_en
    heder: str 
    heder_dict: Any | None
    body: Any | None

