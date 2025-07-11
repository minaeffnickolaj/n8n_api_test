import os
import httpx
from openai import AsyncOpenAI
from fastapi import HTTPException

from issue_api.models.issue import Issue, IssueResponse


class AI:
    def __init__(self) -> None:
        if os.getenv("OPENAI_TOKEN") is None:
            raise EnvironmentError("Не установлена переменная токена OpenAI API")
        else:
            self._token = os.getenv("OPENAI_TOKEN")
        self._client = AsyncOpenAI(api_key=self._token)


    async def get_category(self, payload: Issue) -> str:
        try:
            prompt = (
                f'Определи категорию жалобы: {payload.text}. Варианты: technical, payment, other. Ответ только одним словом.'
            )
            r = await self._client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content" : "Ты помощник по определению категорий жалоб"},
                    {"role" : "user", "content" : prompt}
                ],
                max_tokens=10,
                temperature=0.0 #детерминируем
            )
            return r.choices[0].message.content.strip().lower() #type: ignore
        except :
            return "other" #не стоит падать из-за недоступности, ответим дефолтным значением