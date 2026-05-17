# 超级家长 AI — B2B 家校共育智能平台

为幼儿园/中小学/教培机构提供 AI 驱动的家校共育服务。

## 技术栈
- Python FastAPI
- OpenAI GPT-4o
- JSON 文件存储

## 快速开始

```bash
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 LLM_API_KEY
uvicorn src.api.main:app --reload --port 8000
```

## 项目结构
```
src/
├── api/        # API 层 (main.py + security.py)
├── core/       # 核心业务逻辑
├── ai/         # AI 组件 (LLM + Prompts)
└── utils/      # 工具函数
tests/
├── unit/       # 单元测试
├── integration/ # 集成测试
└── eval/       # AI 评估测试
docs/           # 文档
config/         # 配置
data/           # JSON 数据文件
```
