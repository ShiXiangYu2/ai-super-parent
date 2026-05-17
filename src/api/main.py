"""FastAPI 应用 — 超级家长 AI SaaS 版"""
import json
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from src.api.security import add_security_middleware
from src.ai.client import extract_json, generate_communication_draft, generate_report, get_parenting_advice
from src.core.auth import create_token, get_current_user, get_tenant_id, require_role
from src.core.database import (
    count_by_table, create_class, create_student, create_tenant, create_user, get_class,
    get_student, get_tenant, get_user_by_email, init_db, list_advice_by_student, list_classes,
    list_reports, list_students_by_class, list_students_by_tenant, list_tenants,
    list_users_by_tenant, save_advice, save_report,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ── 结构化日志 ──
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, ensure_ascii=False)

_handler = logging.StreamHandler()
_handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[_handler], force=True)
logger = logging.getLogger("ai-super-parent")

# ── 应用启动 ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ai-super-parent SaaS 启动")
    init_db()
    _seed_demo_data()
    yield
    logger.info("ai-super-parent SaaS 关闭")

app = FastAPI(
    title="ai-super-parent",
    description="超级家长 AI — B2B SaaS 家校共育智能平台",
    version="0.2.0",
    lifespan=lifespan,
)
add_security_middleware(app)

app_metrics = {"start_time": time.time(), "request_count": 0, "error_count": 0}

# ── 前端配置 ──
templates_dir = BASE_DIR / "src" / "web" / "templates"
templates_dir.mkdir(parents=True, exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))

# ── 可观测性中间件 ──
@app.middleware("http")
async def request_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.time()
    app_metrics["request_count"] += 1
    try:
        response = await call_next(request)
        elapsed_ms = (time.time() - start) * 1000
        logger.info(f"request_id={request_id} method={request.method} path={request.url.path} status={response.status_code} latency_ms={elapsed_ms:.1f}")
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as e:
        elapsed_ms = (time.time() - start) * 1000
        app_metrics["error_count"] += 1
        logger.error(f"request_id={request_id} method={request.method} path={request.url.path} error={str(e)} latency_ms={elapsed_ms:.1f}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# ── 种子数据 ──
def _seed_demo_data():
    from src.core.database import get_db
    with get_db() as db:
        existing = db.execute("SELECT COUNT(*) as c FROM tenants").fetchone()
        if existing and existing["c"] > 0:
            return

    tenant = create_tenant("阳光幼儿园", "kindergarten", "北京市朝阳区", "王园长", "13800000000")
    tid = tenant["id"]
    admin = create_user(tid, "王园长", "admin@demo.com", "admin123", "super_admin")
    teacher = create_user(tid, "张老师", "teacher@demo.com", "teacher123", "teacher")
    parent = create_user(tid, "小明妈妈", "parent@demo.com", "parent123", "parent")
    parent2 = create_user(tid, "小红爸爸", "parent2@demo.com", "parent123", "parent")
    cls = create_class(tid, "小班(1班)", "小班", [teacher["id"]])
    cls2 = create_class(tid, "中班(1班)", "中班", [teacher["id"]])
    create_student(tid, cls["id"], "小明", "2021-03-15", "male", parent["id"])
    create_student(tid, cls["id"], "小红", "2021-07-20", "female", parent2["id"])
    create_student(tid, cls2["id"], "小刚", "2020-05-10", "male", parent["id"])
    logger.info("种子数据已初始化 — 演示账号: admin@demo.com/admin123")

# ═══════════════════════════════════════════
# 系统端点
# ═══════════════════════════════════════════
@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "service": "ai-super-parent", "version": "0.2.0",
            "uptime_seconds": int(time.time() - app_metrics["start_time"]),
            "request_count": app_metrics["request_count"]}

@app.get("/metrics", tags=["System"])
async def metrics():
    uptime = time.time() - app_metrics["start_time"]
    return {"uptime_seconds": uptime, "request_count": app_metrics["request_count"],
            "error_rate": round(app_metrics["error_count"] / max(app_metrics["request_count"], 1), 4),
            "avg_latency_ms": 0.0}

# ═══════════════════════════════════════════
# 认证 API
# ═══════════════════════════════════════════
from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str
    tenant_id: str = ""

@app.post("/api/v1/auth/login", tags=["Auth"])
async def login(req: LoginRequest):
    from src.core.database import get_user_by_email_any_tenant, verify_password
    if req.tenant_id:
        user = get_user_by_email(req.tenant_id, req.email)
    else:
        user = get_user_by_email_any_tenant(req.email)
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    token = create_token(user["id"], user["tenant_id"], user["role"], user["name"])
    return {"token": token, "user": {"id": user["id"], "name": user["name"],
            "email": user["email"], "role": user["role"], "tenant_id": user["tenant_id"]}}

@app.get("/api/v1/auth/me", tags=["Auth"])
async def get_me(current_user: dict = Depends(get_current_user)):
    return {"id": current_user["id"], "name": current_user["name"],
            "email": current_user["email"], "role": current_user["role"],
            "tenant_id": current_user["tenant_id"]}

# ═══════════════════════════════════════════
# 机构管理
# ═══════════════════════════════════════════
@app.get("/api/v1/tenant", tags=["机构管理"])
async def get_tenant_info(cu: dict = Depends(require_role("tenant_admin")), tid: str = Depends(get_tenant_id)):
    t = get_tenant(tid)
    if not t:
        raise HTTPException(status_code=404, detail="机构不存在")
    return t

@app.get("/api/v1/tenant/stats", tags=["机构管理"])
async def get_tenant_stats(cu: dict = Depends(require_role("tenant_admin")), tid: str = Depends(get_tenant_id)):
    return {"student_count": count_by_table(tid, "students"), "class_count": count_by_table(tid, "classes"),
            "teacher_count": count_by_table(tid, "users"),
            "advice_count": count_by_table(tid, "advice_records")}

# ═══════════════════════════════════════════
# 班级管理
# ═══════════════════════════════════════════
@app.get("/api/v1/classes", tags=["班级管理"])
async def get_classes(cu: dict = Depends(require_role("teacher")), tid: str = Depends(get_tenant_id)):
    return {"classes": list_classes(tid)}

@app.post("/api/v1/classes", tags=["班级管理"])
async def add_class(req: Request, cu: dict = Depends(require_role("tenant_admin")), tid: str = Depends(get_tenant_id)):
    body = await req.json()
    return create_class(tid, body["name"], body.get("grade", ""), body.get("teacher_ids", []))

@app.get("/api/v1/classes/{class_id}/students", tags=["班级管理"])
async def get_class_students(class_id: str, cu: dict = Depends(require_role("teacher")), tid: str = Depends(get_tenant_id)):
    cls = get_class(class_id)
    if not cls or cls["tenant_id"] != tid:
        raise HTTPException(status_code=404, detail="班级不存在")
    return {"students": list_students_by_class(class_id)}

# ═══════════════════════════════════════════
# 学生管理
# ═══════════════════════════════════════════
@app.post("/api/v1/students", tags=["学生管理"])
async def add_student(req: Request, cu: dict = Depends(require_role("teacher")), tid: str = Depends(get_tenant_id)):
    body = await req.json()
    return create_student(tid, body["class_id"], body["name"], body.get("birth_date", ""), body.get("gender", ""), body.get("parent_user_id", ""))

@app.get("/api/v1/students", tags=["学生管理"])
async def list_students(cu: dict = Depends(require_role("teacher")), tid: str = Depends(get_tenant_id)):
    return {"students": list_students_by_tenant(tid)}

# ═══════════════════════════════════════════
# AI 育儿问答
# ═══════════════════════════════════════════
@app.post("/api/v1/advice", tags=["AI 育儿问答"])
async def advice(req: Request, cu: dict = Depends(require_role("parent")), tid: str = Depends(get_tenant_id)):
    body = await req.json()
    student = get_student(body["student_id"])
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    if cu["role"] == "parent" and student["parent_user_id"] != cu["id"]:
        raise HTTPException(status_code=403, detail="只能查询自己孩子的信息")
    child_age = 0.0
    if student.get("birth_date", ""):
        try:
            child_age = (datetime.now() - datetime.strptime(student["birth_date"], "%Y-%m-%d")).days / 365.25
        except ValueError:
            pass
    answer = get_parenting_advice(body["question"], child_age, body.get("context", ""))
    return save_advice(tid, student["id"], cu["id"], body["question"], answer, round(child_age, 1))

# ═══════════════════════════════════════════
# 成长报告
# ═══════════════════════════════════════════
@app.post("/api/v1/reports/generate", tags=["成长报告"])
async def generate_report_endpoint(req: Request, cu: dict = Depends(require_role("parent")), tid: str = Depends(get_tenant_id)):
    body = await req.json()
    student = get_student(body["student_id"])
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    if cu["role"] == "parent" and student["parent_user_id"] != cu["id"]:
        raise HTTPException(status_code=403, detail="只能查询自己孩子的信息")
    month = body.get("month", datetime.now().strftime("%Y-%m"))
    raw = generate_report(student.get("name", ""), 0.0, month)
    parsed = extract_json(raw) or {"dimensions": [], "summary": "孩子本月表现良好。", "suggestions": "保持当前节奏。"}
    return save_report(tid, student["id"], month, parsed.get("dimensions", []), parsed.get("summary", ""), parsed.get("suggestions", ""))

@app.get("/api/v1/reports/{student_id}", tags=["成长报告"])
async def get_reports_endpoint(student_id: str, cu: dict = Depends(require_role("parent")), tid: str = Depends(get_tenant_id)):
    student = get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    if cu["role"] == "parent" and student["parent_user_id"] != cu["id"]:
        raise HTTPException(status_code=403, detail="只能查询自己孩子的信息")
    return {"reports": list_reports(student_id)}

# ═══════════════════════════════════════════
# 评语辅助
# ═══════════════════════════════════════════
@app.post("/api/v1/communication/draft", tags=["评语辅助"])
async def communication_draft(req: Request, cu: dict = Depends(require_role("teacher")), tid: str = Depends(get_tenant_id)):
    body = await req.json()
    student = get_student(body["student_id"])
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    child_age = 0.0
    if student.get("birth_date", ""):
        try:
            child_age = (datetime.now() - datetime.strptime(student["birth_date"], "%Y-%m-%d")).days / 365.25
        except ValueError:
            pass
    draft = generate_communication_draft(student.get("name", ""), child_age, body.get("scenario", "comment"), body.get("highlights", ""), body.get("tone", "warm"))
    return {"draft": draft}

# ═══════════════════════════════════════════
# 家长端 API
# ═══════════════════════════════════════════
@app.get("/api/v1/my/children", tags=["家长端"])
async def my_children(cu: dict = Depends(require_role("parent"))):
    from src.core.database import list_students_by_parent
    children = list_students_by_parent(cu["id"])
    for c in children:
        reports = list_reports(c["id"])
        c["report_count"] = len(reports)
    return {"children": children}

@app.get("/api/v1/my/advice", tags=["家长端"])
async def my_advice(cu: dict = Depends(require_role("parent"))):
    from src.core.database import list_students_by_parent
    children = list_students_by_parent(cu["id"])
    all_records = []
    for c in children:
        records = list_advice_by_student(c["id"])
        for r in records:
            r["student_name"] = c["name"]
        all_records.extend(records)
    all_records.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"records": all_records}

# ═══════════════════════════════════════════
# 教师端 API
# ═══════════════════════════════════════════
@app.get("/api/v1/teacher/students", tags=["教师端"])
async def teacher_students(cu: dict = Depends(require_role("teacher")), tid: str = Depends(get_tenant_id)):
    classes = list_classes(tid)
    return {"classes": [{"class": c, "students": list_students_by_class(c["id"])} for c in classes]}

# ═══════════════════════════════════════════
# 管理后台 API (super_admin)
# ═══════════════════════════════════════════
@app.get("/api/v1/admin/tenants", tags=["管理后台"])
async def admin_list_tenants(cu: dict = Depends(require_role("super_admin"))):
    return {"tenants": list_tenants()}

@app.post("/api/v1/admin/tenants", tags=["管理后台"])
async def admin_create_tenant(req: Request, cu: dict = Depends(require_role("super_admin"))):
    body = await req.json()
    tenant = create_tenant(body["name"], body.get("org_type", "kindergarten"), body.get("region", ""), body.get("contact_name", ""), body.get("contact_phone", ""))
    create_user(tenant["id"], body.get("contact_name", "管理员"), body.get("admin_email", f"admin@{tenant['id']}.com"), body.get("admin_password", "admin123"), "tenant_admin")
    return tenant

# ═══════════════════════════════════════════
# 前端页面
# ═══════════════════════════════════════════
@app.get("/", response_class=HTMLResponse, tags=["前端"])
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/app/login", response_class=HTMLResponse, tags=["前端"])
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")

@app.get("/app/dashboard", response_class=HTMLResponse, tags=["前端"])
async def dashboard_page(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")

@app.get("/app/children", response_class=HTMLResponse, tags=["前端"])
async def children_page(request: Request):
    return templates.TemplateResponse(request, "children.html")

@app.get("/app/advice", response_class=HTMLResponse, tags=["前端"])
async def advice_page(request: Request):
    return templates.TemplateResponse(request, "advice.html")

@app.get("/app/reports", response_class=HTMLResponse, tags=["前端"])
async def reports_page(request: Request):
    return templates.TemplateResponse(request, "reports.html")

@app.get("/app/classes", response_class=HTMLResponse, tags=["前端"])
async def classes_page(request: Request):
    return templates.TemplateResponse(request, "classes.html")

@app.get("/app/teacher", response_class=HTMLResponse, tags=["前端"])
async def teacher_page(request: Request):
    return templates.TemplateResponse(request, "teacher.html")

@app.get("/app/admin", response_class=HTMLResponse, tags=["前端"])
async def admin_page(request: Request):
    return templates.TemplateResponse(request, "admin.html")
