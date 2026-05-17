FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖（仅健康检查需要 curl）
RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data

ENV APP_ENV=production
ENV DB_PATH=/data/app.db

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -sf http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
