# 超级家长 AI — B2B SaaS 家校共育智能平台

每个孩子，都有一个 AI 育儿顾问。每位教师，都有一个 AI 协作助手。

## 快速体验

```bash
# 一键启动 Demo（macOS / Linux）
bash demo.sh

# 浏览器访问
open http://localhost:8000
```

**Demo 账号：**

| 角色 | 邮箱 | 密码 | 功能 |
|------|------|------|------|
| 👑 平台管理员 | admin@demo.com | admin123 | 多机构管理、租户管理 |
| 👨‍🏫 教师 | teacher@demo.com | teacher123 | 班级管理、AI 评语辅助 |
| 👪 家长 | parent@demo.com | parent123 | AI 育儿问答、成长报告 |

## 核心功能

### 🤖 AI 育儿问答

基于孩子年龄和发展阶段，提供个性化的育儿建议。支持情绪管理、学习习惯、社交能力等多场景问答。

### 📊 成长报告

每月自动生成多维度发展报告，覆盖认知能力、语言发展、社交情感、身体运动、艺术素养五大维度。AI 撰写综合评语和改进建议。

### 💬 评语辅助

AI 辅助教师撰写个性化家长沟通内容，支持多种语气（温暖、正式、鼓励）和场景（评语、通知、家访记录）。

### 👑 多租户管理

平台管理员可在后台管理多个机构（幼儿园/小学），每个机构数据完全隔离，支持订阅管理和用量统计。

## 技术栈

- **后端**: Python 3.12+, FastAPI, SQLite
- **认证**: JWT Token + RBAC 角色权限（super_admin > tenant_admin > teacher > parent）
- **前端**: Jinja2 服务器端渲染 + Tailwind CSS
- **AI**: OpenAI API (GPT-4o-mini)，支持 Mock 模式（无需 API Key 即可体验）
- **可观测性**: 结构化日志、请求追踪、/metrics 端点
- **部署**: Docker, Docker Compose

## 快速开始

### 本地运行

```bash
# 1. 克隆
git clone https://github.com/ShiXiangYu2/ai-super-parent.git
cd ai-super-parent

# 2. 安装依赖
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. 启动（自动生成种子数据）
uvicorn src.api.main:app --reload --port 8000

# 4. 访问
open http://localhost:8000
```

### Docker 部署

```bash
docker compose up -d
```

首次启动会自动初始化数据库和种子数据。

### 配置 LLM API

编辑 `.env` 文件，或在环境变量中设置：

```bash
export LLM_API_KEY=sk-your-key-here
export LLM_MODEL=gpt-4o-mini
```

> **未配置 API Key 时，AI 功能返回 Mock 数据**，所有功能仍可正常体验。

## 项目结构

```
src/
├── api/
│   ├── main.py       # 33 个 API 路由 + 9 个前端页面
│   ├── models.py     # Pydantic 数据模型
│   └── security.py   # CORS + 安全中间件
├── core/
│   ├── database.py   # SQLite 多租户数据层
│   ├── auth.py       # JWT 认证 + RBAC 角色权限
│   └── storage.py    # (legacy) JSON 文件存储
├── ai/
│   └── client.py     # LLM 客户端 + Mock 模式
└── web/templates/    # 10 个 Jinja2 模板
    ├── base.html     # 布局 + 导航 + JWT 自动解码
    ├── login.html    # 一键切换角色登录
    ├── dashboard.html
    ├── advice.html   # AI 育儿问答
    ├── reports.html  # 成长报告
    ├── teacher.html  # 教师端
    ├── admin.html    # 管理后台
    └── ...
tests/
├── unit/             # 6 个单元测试
├── integration/      # 8 个集成测试
└── eval/             # 18 个 AI 评估测试
scripts/
└── demo_seed.py     # Demo 数据生成脚本
```

## API 概览

| 分组 | 端点 | 说明 |
|------|------|------|
| 系统 | GET /health, /metrics | 健康检查、运行指标 |
| 认证 | POST /api/v1/auth/login, GET /api/v1/auth/me | JWT 登录、获取当前用户 |
| 机构 | GET /api/v1/tenant, /api/v1/tenant/stats | 机构信息、统计数据 |
| 班级 | GET/POST /api/v1/classes, GET .../{id}/students | 班级 CRUD |
| 学生 | GET/POST /api/v1/students | 学生管理 |
| AI 问答 | POST /api/v1/advice | AI 育儿问答 |
| 成长报告 | POST /api/v1/reports/generate, GET /api/v1/reports/{id} | 报告生成与查询 |
| 评语辅助 | POST /api/v1/communication/draft | AI 生成家长沟通内容 |
| 家长端 | GET /api/v1/my/children, /api/v1/my/advice | 我的孩子、问答记录 |
| 教师端 | GET /api/v1/teacher/students | 班级学生一览 |
| 管理后台 | GET/POST /api/v1/admin/tenants | 租户管理 |

完整 API 文档见 [docs/api.md](docs/api.md)。

## 运行测试

```bash
# 全部测试 (32 个)
pytest -v

# 按类别
pytest tests/unit/ -v        # 单元测试
pytest tests/integration/ -v # 集成测试
pytest tests/eval/ -v        # AI 评估测试
```
