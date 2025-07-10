from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse

from issue_api.models.issue import IssueRequest, IssueResponse, Issue
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
    except Exception as e :
        raise Exception(e)