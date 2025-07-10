import pytest
from pydantic import ValidationError
from datetime import datetime
from issue_api.models.issue import Issue, IssueRequest, IssueResponse  # Предполагается, что модели находятся в модуле models

# Тесты для модели Issue
def test_issue_valid_data():
    issue = Issue(
        id=1,
        text="Valid text",
        status="open",
        timestamp=datetime.now(),
        sentiment="positive",
        category="technical"
    )
    assert issue.id == 1
    assert issue.text == "Valid text"
    assert issue.status == "open"
    assert issue.sentiment == "positive"
    assert issue.category == "technical"

def test_issue_empty_text():
    with pytest.raises(ValidationError, match="Ошибка валидации поля, пустое значение"):
        Issue(
            id=1,
            text="",
            status="open",
            timestamp=datetime.now(),
            sentiment="positive",
            category="technical"
        )

def test_issue_invalid_status():
    with pytest.raises(ValidationError, match="Недопустимое значение поля статуса - допустимы open или closed"):
        Issue(
            id=1,
            text="Valid text",
            status="invalid",
            timestamp=datetime.now(),
            sentiment="positive",
            category="technical"
        )

def test_issue_invalid_sentiment():
    with pytest.raises(ValidationError, match="Недопустимое значение поля sentiment - допустимы positive, negative, neutral, unknown"):
        Issue(
            id=1,
            text="Valid text",
            status="open",
            timestamp=datetime.now(),
            sentiment="invalid",
            category="technical"
        )

def test_issue_invalid_category():
    with pytest.raises(ValueError, match="Недопустимое значение поля category - допустимы technical, payment, other"):
        Issue(
            id=1,
            text="Valid text",
            status="open",
            timestamp=datetime.now(),
            sentiment="positive",
            category="invalid"
        )

def test_issue_request_empty_text():
    with pytest.raises(ValueError, match="Ошибка валидации поля, пустое значение"):
        IssueRequest(text="")

# Тесты для модели IssueResponse
def test_issue_response_valid_data():
    response = IssueResponse(
        id=1
    )
    assert response.id == 1
    assert response.status == "open"
    assert response.sentiment == "unknown"
    assert response.category == "other"

def test_issue_response_invalid_status():
    with pytest.raises(ValueError, match="Недопустимое значение поля статуса - допустимы open или closed"):
        IssueResponse(
            id=1,
            status="invalid"
        )

def test_issue_response_invalid_sentiment():
    with pytest.raises(ValidationError, match="Недопустимое значение поля sentiment - допустимы positive, negative, neutral, unknown"):
        IssueResponse(
            id=1,
            text="Valid text",
            status="open",
            timestamp=datetime.now(),
            sentiment="invalid"
        )

def test_issue_response_invalid_category():
    with pytest.raises(ValueError, match="Недопустимое значение поля category - допустимы technical, payment, other"):
        IssueResponse(
            id=1,
            category="invalid"
        )

# Тесты для проверки значений по умолчанию в IssueResponse
def test_issue_response_default_values():
    response = IssueResponse(
        id=1
    )
    assert response.status == "open"
    assert response.sentiment == "unknown"
    assert response.category == "other"

# Тесты для проверки ORM-маппинга
def test_issue_from_orm():
    class MockIssue:
        def __init__(self):
            self.id = 1
            self.text = "Valid text"
            self.status = "open"
            self.timestamp = datetime.now()
            self.sentiment = "positive"
            self.category = "technical"

    mock_issue = MockIssue()
    issue = Issue.model_validate(mock_issue)
    assert issue.id == 1
    assert issue.text == "Valid text"
    assert issue.status == "open"
    assert issue.sentiment == "positive"
    assert issue.category == "technical"

def test_issue_response_from_orm():
    class MockIssue:
        def __init__(self):
            self.id = 1
            self.text = "Valid text"
            self.status = "closed"
            self.timestamp = datetime.now()
            self.sentiment = "negative"
            self.category = "payment"

    mock_issue = MockIssue()
    response = IssueResponse.model_validate(mock_issue)
    assert response.id == 1
    assert response.status == "closed"
    assert response.sentiment == "negative"
    assert response.category == "payment"