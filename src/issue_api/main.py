from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse

from issue_api.models.issue import IssueRequest, IssueResponse, Issue
from issue_api.utils.sentiment import SentimentAPI
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
            return await db_conn_provider.insert(r)
    except :
        pass