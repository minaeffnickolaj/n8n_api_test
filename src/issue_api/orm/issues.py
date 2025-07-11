from sqlalchemy import Column, String, Integer, DateTime, update, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declarative_base

from datetime import datetime
from typing import List

import os # доступ к энвам контейнера

from issue_api.models.issue import Issue, IssueResponse

SQLITE_FALLBACK_DBPATH = './app.db'

class Database(AsyncAttrs,DeclarativeBase):
    pass

class Issues(Database):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, index=True, nullable=False, default="open")
    timestamp = Column(DateTime, index=True, nullable=False, default=datetime.now())
    category = Column(String, nullable=False, default="other")
    sentiment = Column(String, nullable=False)
    text = Column(String, nullable=False)

class IssuesProvider:
    def __init__(self) -> None:

        self._dbaddr = os.getenv('SQLITE_DB_PATH', SQLITE_FALLBACK_DBPATH)

        if not os.path.exists(self._dbaddr):
            with open(self._dbaddr, 'a') as f:
                pass  #пустышка

        self._engine = create_async_engine(f'sqlite+aiosqlite:///{self._dbaddr}')
        self._session : async_sessionmaker[AsyncSession] = async_sessionmaker(self._engine)

    async def init_db(self): ## инитим базу из метаданных
        async with self._engine.begin() as conn:
             await conn.run_sync(Database.metadata.create_all)

    async def insert(self, issue : Issue) -> Issue: 
        async with self._session() as s:
            async with s.begin():
                issue_data = issue.model_dump(exclude={'id', 'timestamp'})

                db_issue = Issues(**issue_data)
                s.add(db_issue)

                await s.flush()
                await s.refresh(db_issue)

                return Issue(
                    id=db_issue.id, # type: ignore
                    status=issue_data['status'],
                    timestamp=db_issue.timestamp, #type: ignore
                    category=issue_data['category'],
                    sentiment=issue_data['sentiment'],
                    text=issue_data['text']
                ) 

    async def update(self, issue: Issue) -> Issue | None:
        async with self._session() as s:
            async with s.begin():
                issue_data = issue.model_dump(exclude={'id'})
                stmt = (
                    update(Issues)
                    .where(Issues.id == issue.id)
                    .values(**issue_data)
                )
                result = await s.execute(stmt)
                if result.rowcount == 0:
                    return None
                db_issue = await s.get(Issues, issue.id)
                if db_issue is None:
                    return None
                return Issue(
                    id=db_issue.id, #type: ignore
                    status=db_issue.status,#type: ignore
                    timestamp=db_issue.timestamp,#type: ignore
                    category=db_issue.category,#type: ignore
                    sentiment=db_issue.sentiment,#type: ignore
                    text= db_issue.text #type: ignore
                )
            
    async def select(self, created_at : datetime, status : str = "open") -> List[IssueResponse]:
        async with self._session() as s:
            async with s.begin():
                stmt = select(Issues).where(
                    Issues.status == "open",
                    Issues.timestamp >= created_at
                )
                result = await s.execute(stmt)
                issues = result.scalars().all()

                result_issues = [
                    IssueResponse(**Issue(
                        id=issue.id, #type: ignore
                        status=issue.status, #type: ignore
                        timestamp=issue.timestamp, #type: ignore
                        category=issue.category, #type: ignore
                        sentiment=issue.sentiment, #type: ignore
                        text=issue.text #type: ignore
                    ).model_dump()) for issue in issues
                ]

                return result_issues
                
    async def close_issue(self, id : int) -> bool:
        async with self._session() as s:
            async with s.begin():
                stmt = (
                    update(Issues)
                    .where(Issues.id == id)
                    .values(status = "closed")
                )
                
                result = await s.execute(stmt)
                await s.commit()

                if result.rowcount == 0:
                    return False
                return True