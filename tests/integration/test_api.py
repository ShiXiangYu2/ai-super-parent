"""集成测试 — 超级家长 AI API (SaaS 版)"""
import json
import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

# 在 import main 前设置测试环境
os.environ["API_TOKEN"] = "test-token"
os.environ["CORS_ORIGINS"] = "*"
os.environ["JWT_SECRET"] = "test-jwt-secret"
os.environ["DB_PATH"] = "/tmp/test_int_super_parent.db"

import pathlib
pathlib.Path("/tmp/test_int_super_parent.db").unlink(missing_ok=True)

from src.api.main import app, app_metrics

app_metrics["start_time"] = 12345.0
app_metrics["request_count"] = 0
app_metrics["error_count"] = 0


class TestSystem(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_returns_200(self):
        with self.client as c:
            resp = c.get("/health")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertEqual(data["status"], "ok")
            self.assertEqual(data["service"], "ai-super-parent")
            self.assertIn("uptime_seconds", data)
            self.assertIn("request_count", data)

    def test_metrics_returns_200(self):
        with self.client as c:
            resp = c.get("/metrics")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertIn("uptime_seconds", data)
            self.assertIn("request_count", data)
            self.assertIn("error_rate", data)
            self.assertIn("avg_latency_ms", data)


class TestAuth(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_login_success_without_tenant_id(self):
        with self.client as c:
            resp = c.post("/api/v1/auth/login", json={
                "email": "parent@demo.com", "password": "parent123", "tenant_id": ""
            })
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertIn("token", data)
            self.assertEqual(data["user"]["role"], "parent")

    def test_login_wrong_password_returns_401(self):
        with self.client as c:
            resp = c.post("/api/v1/auth/login", json={
                "email": "parent@demo.com", "password": "wrong", "tenant_id": ""
            })
            self.assertEqual(resp.status_code, 401)

    def test_no_token_returns_401(self):
        with self.client as c:
            resp = c.post("/api/v1/advice", json={"student_id": "x", "question": "test"})
            self.assertEqual(resp.status_code, 401)

    def test_wrong_token_returns_401(self):
        with self.client as c:
            resp = c.post(
                "/api/v1/advice",
                json={"student_id": "x", "question": "test"},
                headers={"Authorization": "Bearer invalid-jwt-token"},
            )
            self.assertEqual(resp.status_code, 401)


class TestAdviceEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.token = None

    def _login(self):
        if self.token:
            return self.token
        with self.client as c:
            r = c.post("/api/v1/auth/login", json={
                "email": "parent@demo.com", "password": "parent123", "tenant_id": ""
            })
            self.token = r.json()["token"]
        return self.token

    @patch("src.api.main.get_parenting_advice")
    def test_advice_returns_mock(self, mock_advice):
        mock_advice.return_value = "这是一条测试育儿建议。"
        tok = self._login()
        with self.client as c:
            # Get actual student ID
            r = c.get("/api/v1/my/children", headers={"Authorization": f"Bearer {tok}"})
            children = r.json().get("children", [])
            if not children:
                self.skipTest("no children found in seed data")
            student_id = children[0]["id"]
            resp = c.post(
                "/api/v1/advice",
                json={"student_id": student_id, "question": "孩子不爱吃饭怎么办？"},
                headers={"Authorization": f"Bearer {tok}"},
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertIn("answer", data)
            self.assertIn("child_age", data)

    def test_advice_nonexistent_student(self):
        tok = self._login()
        with self.client as c:
            resp = c.post(
                "/api/v1/advice",
                json={"student_id": "nonexistent", "question": "test"},
                headers={"Authorization": f"Bearer {tok}"},
            )
            self.assertEqual(resp.status_code, 404)


class TestCommunicationEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.token = None

    def _login_teacher(self):
        with self.client as c:
            r = c.post("/api/v1/auth/login", json={
                "email": "teacher@demo.com", "password": "teacher123", "tenant_id": ""
            })
            self.token = r.json()["token"]
        return self.token

    @patch("src.api.main.generate_communication_draft")
    def test_communication_draft(self, mock_draft):
        mock_draft.return_value = "这是一条测试评语。"
        tok = self._login_teacher()
        with self.client as c:
            # Get actual student ID from teacher's classes
            r = c.get("/api/v1/teacher/students", headers={"Authorization": f"Bearer {tok}"})
            classes = r.json().get("classes", [])
            if not classes or not classes[0].get("students"):
                self.skipTest("no students found in seed data")
            student_id = classes[0]["students"][0]["id"]
            resp = c.post(
                "/api/v1/communication/draft",
                json={"student_id": student_id, "scenario": "comment", "highlights": "上课认真", "tone": "warm"},
                headers={"Authorization": f"Bearer {tok}"},
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertIn("draft", data)
            self.assertEqual(data["draft"], "这是一条测试评语。")


class TestReportEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.token = None

    def _login_parent(self):
        with self.client as c:
            r = c.post("/api/v1/auth/login", json={
                "email": "parent@demo.com", "password": "parent123", "tenant_id": ""
            })
            self.token = r.json()["token"]
            self.parent_id = r.json()["user"]["id"]
        return self.token

    @patch("src.api.main.generate_report")
    def test_generate_report(self, mock_report):
        mock_report.return_value = json.dumps({
            "dimensions": [
                {"name": "认知能力", "score": 8.0, "description": "表现优秀"},
                {"name": "社交能力", "score": 7.5, "description": "表现良好"},
            ],
            "summary": "本月表现优秀。",
            "suggestions": "继续保持。",
        })
        tok = self._login_parent()
        with self.client as c:
            # First, get actual student IDs
            r = c.get("/api/v1/my/children", headers={"Authorization": f"Bearer {tok}"})
            children = r.json().get("children", [])
            if not children:
                self.skipTest("no children found in seed data")
            student_id = children[0]["id"]

            resp = c.post(
                "/api/v1/reports/generate",
                json={"student_id": student_id, "month": "2026-05"},
                headers={"Authorization": f"Bearer {tok}"},
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertIn("summary", data)
            self.assertIn("suggestions", data)

    def test_get_reports(self):
        tok = self._login_parent()
        with self.client as c:
            r = c.get("/api/v1/my/children", headers={"Authorization": f"Bearer {tok}"})
            children = r.json().get("children", [])
            if not children:
                self.skipTest("no children found in seed data")
            student_id = children[0]["id"]

            resp = c.get(
                f"/api/v1/reports/{student_id}",
                headers={"Authorization": f"Bearer {tok}"},
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertIn("reports", data)


class TestRoleBasedAccess(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def _login(self, email, pw):
        with self.client as c:
            r = c.post("/api/v1/auth/login", json={
                "email": email, "password": pw, "tenant_id": ""
            })
            return r.json()["token"]

    def test_parent_cannot_access_teacher_endpoint(self):
        tok = self._login("parent@demo.com", "parent123")
        with self.client as c:
            resp = c.get("/api/v1/teacher/students", headers={"Authorization": f"Bearer {tok}"})
            self.assertEqual(resp.status_code, 403)

    def test_teacher_cannot_access_admin_endpoint(self):
        tok = self._login("teacher@demo.com", "teacher123")
        with self.client as c:
            resp = c.get("/api/v1/admin/tenants", headers={"Authorization": f"Bearer {tok}"})
            self.assertEqual(resp.status_code, 403)

    def test_super_admin_can_access_admin_endpoint(self):
        tok = self._login("admin@demo.com", "admin123")
        with self.client as c:
            resp = c.get("/api/v1/admin/tenants", headers={"Authorization": f"Bearer {tok}"})
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertIn("tenants", data)


if __name__ == "__main__":
    unittest.main()
