"""SaaS 级 SQLite 数据库层 — 多租户 + 自动迁移"""
import hashlib
import json
import os
import sqlite3
import threading
from contextlib import contextmanager
from typing import Any, Optional

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "..", "data", "app.db"))

_local = threading.local()


def _get_conn() -> sqlite3.Connection:
    """获取线程级数据库连接。"""
    if not hasattr(_local, "conn") or _local.conn is None:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        _local.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _local.conn.row_factory = sqlite3.Row
        _local.conn.execute("PRAGMA journal_mode=WAL")
        _local.conn.execute("PRAGMA foreign_keys=ON")
    return _local.conn


@contextmanager
def get_db():
    conn = _get_conn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def init_db():
    """初始化数据库表结构。"""
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS tenants (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            org_type TEXT DEFAULT 'kindergarten',
            region TEXT DEFAULT '',
            contact_name TEXT DEFAULT '',
            contact_phone TEXT DEFAULT '',
            subscription_status TEXT DEFAULT 'active',
            max_students INTEGER DEFAULT 200,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('super_admin', 'tenant_admin', 'teacher', 'parent')),
            phone TEXT DEFAULT '',
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(tenant_id, email),
            FOREIGN KEY (tenant_id) REFERENCES tenants(id)
        );

        CREATE TABLE IF NOT EXISTS classes (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            name TEXT NOT NULL,
            grade TEXT DEFAULT '',
            teacher_ids TEXT DEFAULT '[]',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (tenant_id) REFERENCES tenants(id)
        );

        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            class_id TEXT NOT NULL,
            name TEXT NOT NULL,
            birth_date TEXT DEFAULT '',
            gender TEXT DEFAULT '',
            parent_user_id TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (tenant_id) REFERENCES tenants(id),
            FOREIGN KEY (class_id) REFERENCES classes(id)
        );

        CREATE TABLE IF NOT EXISTS advice_records (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            parent_user_id TEXT DEFAULT '',
            question TEXT NOT NULL,
            answer TEXT DEFAULT '',
            child_age REAL DEFAULT 0.0,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (tenant_id) REFERENCES tenants(id)
        );

        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            month TEXT NOT NULL,
            dimensions TEXT DEFAULT '[]',
            summary TEXT DEFAULT '',
            suggestions TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (tenant_id) REFERENCES tenants(id)
        );
        """)


def hash_password(password: str) -> str:
    """简单密码哈希（生产环境应使用 bcrypt）。"""
    return hashlib.sha256(f"super-parent-salt-{password}".encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


# ── 租户操作 ──
def create_tenant(name: str, org_type: str = "kindergarten", region: str = "",
                  contact_name: str = "", contact_phone: str = "") -> dict:
    import uuid
    tid = f"tenant-{uuid.uuid4().hex[:8]}"
    with get_db() as db:
        db.execute(
            "INSERT INTO tenants (id, name, org_type, region, contact_name, contact_phone) VALUES (?, ?, ?, ?, ?, ?)",
            (tid, name, org_type, region, contact_name, contact_phone),
        )
    return {"id": tid, "name": name, "org_type": org_type}


def get_tenant(tenant_id: str) -> Optional[dict]:
    with get_db() as db:
        row = db.execute("SELECT * FROM tenants WHERE id=?", (tenant_id,)).fetchone()
        return dict(row) if row else None


def list_tenants() -> list[dict]:
    with get_db() as db:
        return [dict(r) for r in db.execute("SELECT * FROM tenants ORDER BY created_at DESC").fetchall()]


# ── 用户操作 ──
def create_user(tenant_id: str, name: str, email: str, password: str, role: str, phone: str = "") -> dict:
    import uuid
    uid = f"user-{uuid.uuid4().hex[:8]}"
    pw_hash = hash_password(password)
    with get_db() as db:
        db.execute(
            "INSERT INTO users (id, tenant_id, name, email, password_hash, role, phone) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (uid, tenant_id, name, email, pw_hash, role, phone),
        )
    return {"id": uid, "name": name, "email": email, "role": role}


def get_user_by_email(tenant_id: str, email: str) -> Optional[dict]:
    with get_db() as db:
        row = db.execute("SELECT * FROM users WHERE tenant_id=? AND email=?", (tenant_id, email)).fetchone()
        return dict(row) if row else None


def get_user(user_id: str) -> Optional[dict]:
    with get_db() as db:
        row = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        return dict(row) if row else None


def get_user_by_email_any_tenant(email: str) -> Optional[dict]:
    """跨租户搜索邮箱（用于登录时未知 tenant_id 的场景）。"""
    with get_db() as db:
        row = db.execute("SELECT * FROM users WHERE email=? LIMIT 1", (email,)).fetchone()
        return dict(row) if row else None


def list_users_by_tenant(tenant_id: str) -> list[dict]:
    with get_db() as db:
        rows = db.execute("SELECT id, tenant_id, name, email, role, phone, is_active, created_at FROM users WHERE tenant_id=? ORDER BY created_at DESC", (tenant_id,)).fetchall()
        return [dict(r) for r in rows]


# ── 班级操作 ──
def create_class(tenant_id: str, name: str, grade: str = "", teacher_ids: list[str] = None) -> dict:
    import uuid
    cid = f"class-{uuid.uuid4().hex[:8]}"
    with get_db() as db:
        db.execute(
            "INSERT INTO classes (id, tenant_id, name, grade, teacher_ids) VALUES (?, ?, ?, ?, ?)",
            (cid, tenant_id, name, grade, json.dumps(teacher_ids or [], ensure_ascii=False)),
        )
    return {"id": cid, "name": name, "grade": grade}


def list_classes(tenant_id: str) -> list[dict]:
    with get_db() as db:
        rows = db.execute("SELECT * FROM classes WHERE tenant_id=? ORDER BY created_at DESC", (tenant_id,)).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["teacher_ids"] = json.loads(d.get("teacher_ids", "[]"))
            result.append(d)
        return result


def get_class(class_id: str) -> Optional[dict]:
    with get_db() as db:
        row = db.execute("SELECT * FROM classes WHERE id=?", (class_id,)).fetchone()
        if row:
            d = dict(row)
            d["teacher_ids"] = json.loads(d.get("teacher_ids", "[]"))
            return d
        return None


# ── 学生操作 ──
def create_student(tenant_id: str, class_id: str, name: str, birth_date: str = "",
                   gender: str = "", parent_user_id: str = "") -> dict:
    import uuid
    sid = f"student-{uuid.uuid4().hex[:8]}"
    with get_db() as db:
        db.execute(
            "INSERT INTO students (id, tenant_id, class_id, name, birth_date, gender, parent_user_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (sid, tenant_id, class_id, name, birth_date, gender, parent_user_id),
        )
    return {"id": sid, "name": name, "class_id": class_id}


def get_student(student_id: str) -> Optional[dict]:
    with get_db() as db:
        row = db.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
        return dict(row) if row else None


def list_students_by_class(class_id: str) -> list[dict]:
    with get_db() as db:
        return [dict(r) for r in db.execute("SELECT * FROM students WHERE class_id=? ORDER BY name", (class_id,)).fetchall()]


def list_students_by_tenant(tenant_id: str) -> list[dict]:
    with get_db() as db:
        return [dict(r) for r in db.execute("SELECT * FROM students WHERE tenant_id=? ORDER BY name", (tenant_id,)).fetchall()]


def list_students_by_parent(parent_user_id: str) -> list[dict]:
    with get_db() as db:
        return [dict(r) for r in db.execute("SELECT * FROM students WHERE parent_user_id=? ORDER BY name", (parent_user_id,)).fetchall()]


# ── 育儿问答操作 ──
def save_advice(tenant_id: str, student_id: str, parent_user_id: str,
                question: str, answer: str, child_age: float) -> dict:
    import uuid
    aid = f"advice-{uuid.uuid4().hex[:8]}"
    with get_db() as db:
        db.execute(
            "INSERT INTO advice_records (id, tenant_id, student_id, parent_user_id, question, answer, child_age) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (aid, tenant_id, student_id, parent_user_id, question, answer, child_age),
        )
    return {"id": aid, "answer": answer, "child_age": child_age}


def list_advice_by_student(student_id: str) -> list[dict]:
    with get_db() as db:
        return [dict(r) for r in db.execute("SELECT * FROM advice_records WHERE student_id=? ORDER BY created_at DESC", (student_id,)).fetchall()]


# ── 报告操作 ──
def save_report(tenant_id: str, student_id: str, month: str, dimensions: list,
                summary: str, suggestions: str) -> dict:
    import uuid
    rid = f"report-{uuid.uuid4().hex[:8]}"
    with get_db() as db:
        db.execute(
            "INSERT INTO reports (id, tenant_id, student_id, month, dimensions, summary, suggestions) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (rid, tenant_id, student_id, month, json.dumps(dimensions, ensure_ascii=False), summary, suggestions),
        )
    return {"id": rid, "student_id": student_id, "month": month, "dimensions": dimensions, "summary": summary, "suggestions": suggestions}


def list_reports(student_id: str) -> list[dict]:
    with get_db() as db:
        rows = db.execute("SELECT * FROM reports WHERE student_id=? ORDER BY month DESC", (student_id,)).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["dimensions"] = json.loads(d.get("dimensions", "[]"))
            result.append(d)
        return result


# ── 统计 ──
def count_by_table(tenant_id: str, table: str) -> int:
    with get_db() as db:
        row = db.execute(f"SELECT COUNT(*) as cnt FROM {table} WHERE tenant_id=?", (tenant_id,)).fetchone()
        return row["cnt"] if row else 0
