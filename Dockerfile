FROM python:3.10-alpine
LABEL authors="eve"

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/venv/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r venv/requirements.txt

# Создаем том для хранения данных
VOLUME /usr/src/app/data

COPY . /usr/src/app

CMD ["python", "main.py"]
#docker build -t telegram-pasta-bot .
#docker run -v .\users.txt:/usr/src/app/data/users.txt -d telegram-pasta-bot