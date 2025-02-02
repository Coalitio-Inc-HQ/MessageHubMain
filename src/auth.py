from fastapi import FastAPI, Depends, Request, HTTPException
from src.settings import settings
from src.loging.logging_utility import log, LogMessage,log_en
import datetime

async def verify_api_key(request: Request):
    if settings.API_KEY:
        key = request.headers.get("API-KEY")
        if key:
            if key == settings.API_KEY:
                return key
            else:
                log(LogMessage(time=datetime.datetime.now().isoformat(),heder="Нверный API_KEY.", 
                    heder_dict={},body=
                    {
                        "key": key,
                        "ip": request.client.host,
                    },
                    level=log_en.INFO))
                raise HTTPException(422)
        else:
            raise HTTPException(422)
    else:
        return "Test mode"