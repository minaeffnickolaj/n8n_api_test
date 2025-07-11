ПОРЯДОК ВНЕДРЕНИЯ 

В /deployment разместите .env 

заполнить переменными

SQLITE_PATH= путь в котором будет храниться БД (примонтировать локальную директорию в компоузе к этому пути и база будет персистентна)

API_SENTIMENT_BEARER= токен для SentimentAPI

OPENAI_TOKEN= токен для chatGPT

Деплой проекта 

    cd deployment && docker-compose up -d 
