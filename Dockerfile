FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /auth-service

COPY auth-service /auth-service
COPY scripts/entrypoint.sh /scripts/entrypoint.sh

RUN apt-get update && apt-get install -y netcat-traditional postgresql-client && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    chmod +x /scripts/entrypoint.sh

ENTRYPOINT ["/scripts/entrypoint.sh"]
