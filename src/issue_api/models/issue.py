from pydantic import BaseModel, field_validator, ConfigDict, Field
from datetime import datetime

class Issue(BaseModel):
    id: int | None
    text: str | None
    status: str = "open"
    timestamp: datetime | None
    sentiment: str = "unknown"
    category: str = "other"

    model_config = ConfigDict(
        from_attributes=True
    )

    @field_validator("text", mode="before")
    def validate_text(cls, v: str) -> str:
        if len(v) > 0:
            return v 
        else:
            raise ValueError("Ошибка валидации поля, пустое значение")
        
    @field_validator("status", mode="before")
    def validate_status(cls, v: str) -> str:
        if v in ["open", "closed"]:
            return v
        else:
            raise ValueError("Недопустимое значение поля статуса - допустимы open или closed")
        
    @field_validator("sentiment", mode="before")
    def validate_sentiment(cls, v: str) -> str:
        if v in ["positive", "negative", "neutral", "unknown"]:
            return v
        else:
            raise ValueError("Недопустимое значение поля sentiment - допустимы positive, negative, neutral, unknown")
        
    @field_validator("category", mode="before")
    def validate_category(cls, v: str) -> str:
        if v in ["technical", "payment", "other"]:
            return v
        else:
            raise ValueError("Недопустимое значение поля category - допустимы technical, payment, other")

class IssueRequest(Issue):
    id : int | None = Field(default=None, exclude=True)
    timestamp: datetime | None = Field(default=None, exclude=True)
    text: str | None

class IssueResponse(Issue):
    #исключаем поля
    timestamp: datetime | None = Field(default=None, exclude=True)
    text: str | None = Field(default=None, exclude=True)
    model_config = ConfigDict(
        from_attributes=True
    )

    status: str = "open"
    sentiment: str = "unknown"
    category: str = "other"