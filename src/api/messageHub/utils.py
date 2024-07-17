from httpx import AsyncClient, HTTPStatusError
from typing import Any
from src.loging.logging_utility import log, LogMessage,log_en

async def send_http_request(base_url:str, relative_url:str, json: Any|None):
    async with AsyncClient(base_url=base_url) as clinet:
        try:
            response = await clinet.post(relative_url, json=json)
            response.raise_for_status()
        except HTTPStatusError as error:
            log(LogMessage(time=None,heder=f"Ошибка запроса. {error.response.status_code}", 
                   heder_dict=error.args,body=
                    {
                        "base_url":base_url, 
                        "relative_url":relative_url, 
                        "json":json,
                        "response":error.response.json()
                    },
                    level=log_en.ERROR))
        except Exception as error:
            log(LogMessage(time=None,heder="Неизвестная ошибка.", 
                   heder_dict=error.args,body=
                    {
                        "base_url":base_url, 
                        "relative_url":relative_url, 
                        "json":json
                    },
                    level=log_en.ERROR))