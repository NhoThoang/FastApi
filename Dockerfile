# Base image
FROM python:3.12
WORKDIR /app
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p uploads
COPY .env .
EXPOSE 8000
CMD ["sh", "-c", "uvicorn main:app --host ${APP_HOST} --port ${APP_PORT} --reload"] 