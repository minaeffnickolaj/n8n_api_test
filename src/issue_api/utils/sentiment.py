import os
import httpx
import json
from typing import Dict

from issue_api.models.issue import IssueRequest

URL = "https://api.apilayer.com/sentiment/analysis"

class SentimentAPI:
    def __init__(self) -> None:
        if os.getenv("API_SENTIMENT_BEARER") is None:
            raise EnvironmentError("Не установлена переменная токена sentiment API")
        else:
            self._token = os.getenv("API_SENTIMENT_BEARER")
        self._url = URL

    async def get_sentiment(self, payload: IssueRequest) -> str:
        headers : Dict[str, str]= {"apikey": self._token} # type: ignore
        content = payload.text.encode("utf-8") #type: ignore

        async with httpx.AsyncClient() as client:
            try:
                r = await client.post(self._url, headers=headers, content=content)
                v = r.json() ## каст к джсонке
                return v["sentiment"]
            except:
                return "unknown"