# Base image
FROM python:3.12-slim

# Tạo thư mục làm việc
WORKDIR /app

# Cài đặt các package cần thiết
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt
COPY requirements.txt .

# Cài đặt dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Tạo thư mục uploads nếu chưa có
RUN mkdir -p uploads

# Copy .env file
COPY .env .

# Expose port
EXPOSE 8000

# Command để chạy ứng dụng
CMD ["sh", "-c", "uvicorn main:app --host ${APP_HOST} --port ${APP_PORT} --reload"] 