from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse

from typing import List
from datetime import datetime

from issue_api.models.issue import IssueRequest, IssueResponse, Issue, IssueResponseDetails
from issue_api.utils.sentiment import SentimentAPI
from issue_api.utils.openai import AI
from issue_api.orm.issues import IssuesProvider

app = FastAPI()

sentimentAPI = SentimentAPI()

async def get_issues_provider():
    provider = IssuesProvider()
    await provider.init_db()
    try:
        yield provider
    finally:
        await provider._engine.dispose()  # Закрываем базу по завершении аппки

@app.get("/")
def root():
    return JSONResponse({"state":"ok"})

# создание жалобы
@app.post("/issue", response_model=IssueResponse)
async def create_issue(issue : IssueRequest, db_conn_provider = Depends(get_issues_provider)):
    try:
        sentiment = await sentimentAPI.get_sentiment(issue)
        if sentiment:
            r = Issue(
                id = None,
                text=issue.text,
                sentiment=sentiment,
                timestamp=None
            )
            r : Issue = await db_conn_provider.insert(r)
            category = await AI().get_category(r) # идем в гпт за категорией
            if category:
                r.category = category
                r = await db_conn_provider.update(r)
                return IssueResponse(**r.model_dump())
            else:
                raise HTTPException(status_code=500, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
    except HTTPException as e :
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

# возвращаем открытые жалобы созданные с определенного периода времени (можно и больше 1 часа)    
@app.get("/issues", response_model=List[IssueResponseDetails])
async def return_issues(created_at : str, status : str = "open", db_conn_provider : IssuesProvider = Depends(get_issues_provider)):
    try:
        if status not in ["open", "closed"]:
            raise HTTPException(status_code=400, detail="Допустимые значения status = open, closed")
        if created_at == None:
            raise HTTPException(status_code=400, detail="Не указан начальный интервал")
        
        try: #пробуем кастить строку к таймстампу
            created_at_ts = datetime.fromisoformat(created_at) #type: ignore
            if created_at_ts > datetime.now(created_at_ts.tzinfo):
                raise HTTPException(status_code=400, detail="Укажите момент времени в прошлом!")
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный формат created_at, ожидается ISO 8601")
        
        r = await db_conn_provider.select(created_at=created_at_ts)

        return r
    
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Interval Server Error")

# хук изменения статуса жалобы    
@app.post("/webhook")
async def webhook(id : int, db_conn_provider : IssuesProvider = Depends(get_issues_provider)):
    try:
        result = await db_conn_provider.close_issue(id)
        if not result:
            return JSONResponse({"update" : "false"})
        return JSONResponse({"update" : "true"})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")