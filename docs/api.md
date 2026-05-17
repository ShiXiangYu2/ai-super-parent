# API 文档 — 超级家长 AI

## 基础信息

- **Base URL**: `http://localhost:8000`
- **认证**: Bearer Token（通过 `API_TOKEN` 环境变量配置）
- **请求头**: `Authorization: Bearer <token>`
- **Content-Type**: `application/json`

---

## 系统端点

### GET /health
健康检查。

**响应**:
```json
{
  "status": "ok",
  "service": "ai-super-parent",
  "uptime_seconds": 3600,
  "request_count": 150
}
```

### GET /metrics
运行指标。

**响应**:
```json
{
  "uptime_seconds": 3600,
  "request_count": 150,
  "error_rate": 0.02,
  "avg_latency_ms": 45.2
}
```

---

## AI 育儿问答

### POST /api/v1/advice
家长向 AI 育儿助手提问，AI 根据孩子年龄给出个性化建议。

**请求体**:
```json
{
  "student_id": "student-001",
  "question": "孩子不爱吃饭怎么办？",
  "context": "最近刚上幼儿园"
}
```

**响应**:
```json
{
  "id": "uuid",
  "answer": "根据您孩子的年龄和发展阶段，建议如下：...",
  "child_age": 3.5
}
```

---

## 成长报告

### POST /api/v1/report/generate
生成学生月度发展报告。

**请求体**:
```json
{
  "student_id": "student-001",
  "month": "2026-05"
}
```

**响应**:
```json
{
  "id": "uuid",
  "student_id": "student-001",
  "month": "2026-05",
  "dimensions": [
    {"name": "认知能力", "score": 8.0, "description": "表现优秀"},
    {"name": "社交能力", "score": 7.5, "description": "表现良好"}
  ],
  "summary": "孩子本月表现优秀...",
  "suggestions": "1. 每天安排阅读时间\n2. 多参与集体活动",
  "created_at": "2026-05-17T00:00:00Z"
}
```

### GET /api/v1/report/{student_id}
获取学生历史报告列表。

---

## 评语辅助

### POST /api/v1/communication/draft
AI 辅助撰写家校沟通内容。

**请求体**:
```json
{
  "student_id": "student-001",
  "scenario": "comment",
  "highlights": "上课认真，乐于助人",
  "tone": "warm"
}
```

**tone 可选值**: `warm`（温暖）, `formal`（正式）, `encouraging`（鼓励）

---

## 成长趋势

### GET /api/v1/children/{student_id}/trend
获取学生多维度成长趋势数据。

---

## 学生管理

### POST /api/v1/children
添加学生信息。

**请求体**:
```json
{
  "institution_id": "inst-001",
  "class_id": "class-001",
  "name": "小明",
  "birth_date": "2021-03-15",
  "gender": "male"
}
```
