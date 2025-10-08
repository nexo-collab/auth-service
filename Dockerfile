FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /auth-service

COPY auth-service/requirements.txt /auth-service/requirements.txt
RUN apt-get update && \
    apt-get install -y netcat-traditional postgresql-client && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY auth-service /auth-service

RUN chmod +x /auth-service/entrypoint.sh

ENTRYPOINT ["/auth-service/entrypoint.sh"]
