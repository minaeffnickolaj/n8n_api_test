from pydantic import BaseModel, field_validator, ValidationError

from datetime import datetime

class Issue(BaseModel):
    id : int
    text : str 
    status : str = "open"
    timestamp : datetime
    sentiment : str = "unknown"
    category : str = "other"

    class Config:
        from_attributes = True

    @field_validator("text", mode="before")
    def validate_text(cls, v: str) -> str:
        if len(v) > 0:
           return v 
        else:
            raise ValidationError("Ошибка валидации поля, пустое значение")
        
    @field_validator("status", mode="before")
    def validate_status(cls, v: str) -> str:
        if v in ["open", "closed"]:
            return v
        else:
            raise ValidationError("Недопустимое значение поля статуса - допустим open или closed")
        
    @field_validator("sentiment", mode="before")
    def validate_sentiment(cls, v: str) -> str:
        if v in ["positive", "negative", "neutral", "unknown"]:
            return v
        else:
            raise ValidationError("Недопустимое значение поля sentiment - допустимы positive, negative, neutral, unknown")
        
    @field_validator("sentiment", mode="before")
    def validate_category(cls, v: str) -> str:
        if v in ["technical", "payment", "other"]:
            return v
        else:
            raise ValidationError("Недопустимое значение поля category - допустимы technical, payment, other")

class IssueRequest(Issue):
    text : str

class IssueResponse(Issue):
    id : int
    status : str = "open"
    sentiment : str = "unknown"
    category : str = "other"