# 超级家长 AI — 产品使用指南

> B2B SaaS 家校共育智能平台
> 每个孩子，都有一个 AI 育儿顾问。每位教师，都有一个 AI 协作助手。

---

## 目录

1. [产品概述](#1-产品概述)
2. [快速开始](#2-快速开始)
3. [角色说明](#3-角色说明)
4. [家长端使用指南](#4-家长端使用指南)
5. [教师端使用指南](#5-教师端使用指南)
6. [管理员端使用指南](#6-管理员端使用指南)
7. [API 参考](#7-api-参考)
8. [常见问题](#8-常见问题)

---

## 1. 产品概述

### 1.1 核心功能

| 功能 | 说明 | 适用角色 |
|------|------|---------|
| **AI 育儿问答** | 基于孩子年龄和发展阶段，提供个性化育儿建议。支持情绪管理、学习习惯、社交能力等多场景问答。AI 7×24 小时在线解答。 | 家长 |
| **成长报告** | 每月自动生成多维度发展报告（认知能力、语言发展、社交情感、身体运动、艺术素养），可视化跟踪孩子成长轨迹。 | 家长 |
| **评语辅助** | AI 辅助教师撰写个性化家长沟通内容，支持多种语气（温暖、正式、鼓励）和场景（评语、通知、家访记录）。 | 教师 |
| **多租户管理** | 平台管理员可在后台管理多个机构（幼儿园/小学），每个机构数据完全隔离，支持订阅管理和用量统计。 | 超级管理员 |

### 1.2 适用场景

- **幼儿园 / 托育机构** — 教师撰写幼儿观察记录，家长查看孩子发展报告
- **中小学** — 班主任与家长沟通，AI 辅助生成评语
- **教育培训机构** — 学员成长追踪，家长沟通

---

## 2. 快速开始

### 2.1 一键 Demo 启动（推荐）

```bash
git clone git@github.com:ShiXiangYu2/ai-super-parent.git
cd ai-super-parent/code
bash demo.sh
```

启动后浏览器访问 **http://localhost:8000**

### 2.2 手动启动

```bash
cd ai-super-parent/code
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
rm -f data/app.db
python scripts/demo_seed.py
uvicorn src.api.main:app --reload --port 8000
```

### 2.3 Docker 启动

```bash
cd ai-super-parent/code
docker compose up -d
```

### 2.4 配置 AI 模型（可选）

编辑 `.env` 文件或在环境变量中设置：

```bash
export LLM_API_KEY=sk-your-key-here
export LLM_MODEL=gpt-4o-mini
```

> **未配置 API Key 时，AI 功能自动使用 Mock 模式**，返回真实感十足的模拟数据，所有功能均可正常体验。无需 OpenAI 账号即可运行完整 Demo。

---

## 3. 角色说明

### 3.1 Demo 账号一览

| 角色 | 邮箱 | 密码 | 职责范围 |
|------|------|------|---------|
| 👑 平台管理员 | `admin@demo.com` | `admin123` | 管理所有机构、用户、订阅 |
| 👨‍🏫 教师 | `teacher@demo.com` | `teacher123` | 查看班级、撰写评语 |
| 👪 家长 1（小明妈妈） | `parent@demo.com` | `parent123` | 育儿问答、成长报告 |
| 👪 家长 2（小红爸爸） | `parent2@demo.com` | `parent123` | 育儿问答、成长报告 |
| 👪 家长 3（小华妈妈） | `parent3@demo.com` | `parent123` | 育儿问答、成长报告 |

### 3.2 角色权限层级

```
super_admin (100) — 平台超级管理员
    └── tenant_admin (50) — 机构管理员
            └── teacher (20) — 教师
                    └── parent (10) — 家长
```

权限向下兼容：`super_admin` 可以访问所有端点，`teacher` 可以访问 `parent` 级别的数据。

### 3.3 数据隔离

- 每个机构（tenant）拥有独立的数据库隔离，SQLite 层面通过 `tenant_id` 字段实现
- 家长只能查看自己孩子的数据
- 教师只能查看自己班级的学生
- 平台管理员可以跨机构管理

---

## 4. 家长端使用指南

### 4.1 登录与首页

1. 打开 `http://localhost:8000/app/login`
2. 点击 **"👪 家长"** 快捷登录按钮，自动填充 `parent@demo.com` / `parent123`
3. 登录后进入仪表盘，可看到机构统计数据（学生数、班级数、教师数、问答数）
4. 如果是家长角色，仪表盘下方会显示"我的孩子"列表

### 4.2 查看我的孩子

路径：**首页 → 我的孩子**

- 进入 `/app/children` 查看孩子列表
- 每个孩子卡片显示：姓名、性别、出生日期、报告数量
- 点击"育儿问答"或"成长报告"快捷链接进入对应功能

### 4.3 AI 育儿问答

路径：**首页 → 育儿问答**

操作步骤：

1. **选择孩子** — 从左侧面板选择要咨询的孩子
2. **输入问题** — 在文本框中输入育儿问题，例如：
   - "孩子不爱吃饭怎么办？"
   - "孩子总爱发脾气怎么引导？"
   - "如何培养孩子的阅读习惯？"
   - "孩子分离焦虑严重怎么办？"
3. **提交问题** — 点击"向 AI 提问"按钮
4. **查看回答** — AI 根据孩子年龄和发展阶段生成个性化建议，支持 Markdown 格式
5. **查看历史** — 页面下方显示最近 10 条历史问答记录

**提示**：可以在问题中添加上下文信息，例如"最近刚上幼儿园"，帮助 AI 给出更精准的建议。

### 4.4 成长报告

路径：**首页 → 成长报告**

操作步骤：

1. **选择孩子** — 从下拉菜单中选择要查看的孩子
2. **查看报告** — 页面显示该孩子的所有月度报告
3. **报告内容**：
   - **多维度评分**：认知能力、语言发展、社交情感、身体运动、艺术素养（每项满分 10 分，带进度条可视化）
   - **综合评语**：AI 撰写的月度评估总结
   - **改善建议**：针对性的家庭教育建议
4. **生成新报告** — 点击"生成新报告"按钮，AI 自动生成当月报告

**报告维度说明**：

| 维度 | 评估内容 |
|------|---------|
| 认知能力 | 观察力、记忆力、逻辑思维 |
| 语言发展 | 表达能力、词汇量、沟通意愿 |
| 社交情感 | 同伴关系、情绪管理、分享意识 |
| 身体运动 | 大运动、精细动作、协调能力 |
| 艺术素养 | 绘画、音乐、创造力表现 |

---

## 5. 教师端使用指南

### 5.1 教师登录

1. 打开 `http://localhost:8000/app/login`
2. 点击 **"👨‍🏫 教师"** 快捷登录按钮，自动填充 `teacher@demo.com` / `teacher123`
3. 登录后顶部导航只显示"我的班级"

### 5.2 查看班级与学生

路径：**我的班级 → 班级列表**

- 显示该教师负责的所有班级（Demo 数据：张老师负责小班(1班)）
- 每个班级以卡片形式展示，包含班级名称和年级
- 学生表格：姓名、性别、出生日期

### 5.3 AI 撰写评语

1. 在班级学生列表中，点击学生对应的 **"写评语"** 按钮
2. 在弹出的对话框中输入关键点，例如：`上课认真、乐于助人、进步明显`
3. AI 自动生成一段温暖亲切的家长沟通评语
4. 生成的评语以弹窗显示，可直接复制使用

**支持的评语语气**：
- **温暖亲切**（warm）— 适合日常沟通
- **正式专业**（formal）— 适合正式通知
- **鼓励肯定**（encouraging）— 适合鼓励学生

**支持的场景**：评语（comment）、学期总结（review）、家访记录（meeting）

---

## 6. 管理员端使用指南

### 6.1 平台管理员登录

1. 打开 `http://localhost:8000/app/login`
2. 点击 **"👑 平台管理员"** 快捷登录按钮
3. 登录后导航显示"管理后台"

### 6.2 机构管理

路径：**首页 → 管理后台**

功能：
- **查看机构列表** — 显示所有已注册机构（Demo 中默认包含"阳光幼儿园"和"智慧实验小学"）
- **新增机构** — 点击"+ 新增机构"按钮，输入机构名称即可创建
- **机构信息** — 每个机构卡片显示：名称、类型（幼儿园/小学）、地区、联系人、订阅状态、最大学生数

### 6.3 机构统计

路径：**首页 → 仪表盘**

- 查看当前机构的统计数据：
  - 学生数
  - 班级数
  - 教师数
  - AI 问答数

### 6.4 Demo 数据中的机构示例

**阳光幼儿园**（北京市朝阳区）
- 3 个班级：小班(1班)、中班(1班)、大班(1班)
- 12 名学生，含 3 个月预生成的成长报告
- 2 名家长账号关联

**智慧实验小学**（上海市浦东新区）
- 1 个班级：一年级(1班)
- 2 名学生
- 1 名家长账号关联

---

## 7. API 参考

### 7.1 系统端点

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/health` | 健康检查（返回 status、uptime、request_count） | 无 |
| GET | `/metrics` | 运行指标（uptime、request_count、error_rate、avg_latency_ms） | 无 |

### 7.2 认证

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/login` | 登录，返回 JWT Token |
| GET | `/api/v1/auth/me` | 获取当前用户信息 |

**登录请求示例**：

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"parent@demo.com","password":"parent123","tenant_id":""}'
```

**响应示例**：

```json
{
  "token": "eyJhbGci...",
  "user": {
    "id": "user-xxx",
    "name": "小明妈妈",
    "email": "parent@demo.com",
    "role": "parent",
    "tenant_id": "tenant-xxx"
  }
}
```

### 7.3 核心业务 API

| 方法 | 路径 | 说明 | 最低角色 |
|------|------|------|---------|
| POST | `/api/v1/advice` | AI 育儿问答 | parent |
| POST | `/api/v1/reports/generate` | 生成成长报告 | parent |
| GET | `/api/v1/reports/{student_id}` | 查看历史报告 | parent |
| GET | `/api/v1/my/children` | 我的孩子列表 | parent |
| GET | `/api/v1/my/advice` | 我的问答记录 | parent |
| GET | `/api/v1/teacher/students` | 班级学生一览（教师端） | teacher |
| POST | `/api/v1/communication/draft` | AI 生成家长沟通内容 | teacher |
| GET | `/api/v1/classes` | 班级列表 | teacher |
| POST | `/api/v1/classes` | 创建班级 | tenant_admin |
| GET | `/api/v1/tenant/stats` | 机构统计数据 | tenant_admin |
| GET | `/api/v1/admin/tenants` | 所有机构列表（管理后台） | super_admin |
| POST | `/api/v1/admin/tenants` | 创建新机构 | super_admin |

### 7.4 API 认证方式

所有受保护的端点使用 **Bearer Token** 认证：

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/my/children
```

Token 有效期 24 小时，过期后需要重新登录。

### 7.5 前端页面路由

| 路径 | 页面 | 角色 |
|------|------|------|
| `/` | 首页/产品介绍 | 公开 |
| `/app/login` | 登录页 | 公开 |
| `/app/dashboard` | 机构仪表盘 | 全部 |
| `/app/children` | 我的孩子 | parent |
| `/app/advice` | AI 育儿问答 | parent |
| `/app/reports` | 成长报告 | parent |
| `/app/teacher` | 教师端 | teacher |
| `/app/classes` | 班级管理 | tenant_admin |
| `/app/admin` | 管理后台 | super_admin |

---

## 8. 常见问题

### 8.1 启动问题

**Q: 启动时报错 "This environment is externally managed"**

系统 Python 被包管理器（brew/uv）管理。解决方法：

```bash
# 方案一：使用 uv 安装
uv pip install -r requirements.txt

# 方案二：创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Q: 如何重置 Demo 数据？**

```bash
# 删除数据库文件（应用会在下次启动时自动重新生成）
rm -f data/app.db
# 或者使用 demo.sh 启动（自动清理旧数据）
bash demo.sh
```

### 8.2 功能问题

**Q: AI 回答不准确怎么办？**

默认使用 Mock 模式（无需 API Key）。如需真实 AI 回答：

1. 获取 OpenAI API Key
2. 在 `.env` 中设置 `LLM_API_KEY=sk-xxx`
3. 重启应用

**Q: 为什么看不到某些页面？**

每个角色只能看到自己权限范围内的页面：
- 家长看不到"管理后台"
- 教师看不到"育儿问答"
- 管理员看不到"我的孩子"

请使用对应角色的账号登录。

### 8.3 技术问题

**Q: Token 过期了怎么办？**

Token 有效期 24 小时。过期后刷新页面会自动跳转到登录页，重新登录即可。

**Q: 如何切换部署环境？**

编辑 `.env` 文件：

```ini
# 开发环境
APP_ENV=development
APP_DEBUG=true

# 生产环境
APP_ENV=production
APP_DEBUG=false
JWT_SECRET=your-strong-secret-here
```

**Q: 支持哪些数据库？**

当前使用 SQLite，适合 Demo 和小规模部署。生产环境可迁移至 PostgreSQL，数据库层通过 `src/core/database.py` 的 `get_db()` 函数抽象，替换数据库驱动即可。

---

## 技术架构

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  浏览器      │────▶│  FastAPI     │────▶│  SQLite     │
│  Jinja2     │     │  22 Routes   │     │  7 Tables   │
│  Tailwind   │◀────│  JWT + RBAC  │◀────│  Multi-     │
│             │     │  Middleware  │     │  Tenant     │
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
                    ┌──────▼───────┐
                    │  AI Client   │
                    │  OpenAI/Mock │
                    └──────────────┘
```

### 目录结构

```
code/
├── src/
│   ├── api/main.py       # FastAPI 应用（22 个路由 + 自动种子数据）
│   ├── core/database.py  # SQLite 多租户数据层（7 张表）
│   ├── core/auth.py      # JWT 认证 + RBAC 权限（4 个角色）
│   ├── ai/client.py      # LLM 客户端（OpenAI + Mock 模式）
│   └── web/templates/    # 10 个 Jinja2 前端模板
├── tests/                # 32 个测试（单元 + 集成 + Eval）
├── scripts/demo_seed.py  # 增强种子数据脚本
├── demo.sh               # 一键 Demo 启动脚本
└── Dockerfile            # Docker 部署配置
```

---

> **问题反馈**: https://github.com/ShiXiangYu2/ai-super-parent/issues
> **项目主页**: https://github.com/ShiXiangYu2/ai-super-parent
