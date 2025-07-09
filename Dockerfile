FROM python:3.13.5-slim-bookworm

RUN apt-get update && apt-get install -y curl

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

COPY . /app/

RUN /root/.local/share/pypoetry/venv/bin/poetry install

CMD ["/root/.local/share/pypoetry/venv/bin/poetry", "run", "uvicorn", "issue_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
 
EXPOSE 8000