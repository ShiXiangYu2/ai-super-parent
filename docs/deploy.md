# 部署指南 — 超级家长 AI

## 前置条件

- Python 3.12+
- OpenAI API Key（或兼容 API）

## 快速启动（本地）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入 LLM_API_KEY

# 3. 启动服务
uvicorn src.api.main:app --reload --port 8000

# 4. 访问
curl http://localhost:8000/health
```

## Docker 部署

```bash
# 构建
docker build -t ai-super-parent .

# 运行
docker run -d \
  --name ai-super-parent \
  -p 8000:8000 \
  -e API_TOKEN=your-token \
  -e LLM_API_KEY=your-key \
  -v $(pwd)/data:/app/data \
  ai-super-parent
```

## Docker Compose

```bash
docker compose up -d
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `API_TOKEN` | API 认证 Token | 空（开发模式跳过认证） |
| `LLM_API_KEY` | LLM API Key | 空（使用 mock 响应） |
| `LLM_MODEL` | LLM 模型名 | `gpt-4o-mini` |
| `LLM_BASE_URL` | LLM API 地址 | `https://api.openai.com/v1` |
| `CORS_ORIGINS` | 允许的跨域来源 | `*` |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `DATA_DIR` | 数据文件目录 | `./data` |

## API 测试

```bash
# 健康检查
curl http://localhost:8000/health

# AI 育儿问答
curl -X POST http://localhost:8000/api/v1/advice \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"student_id": "student-001", "question": "孩子不爱吃饭怎么办?"}'

# 生成报告
curl -X POST http://localhost:8000/api/v1/report/generate \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"student_id": "student-001", "month": "2026-05"}'
```
