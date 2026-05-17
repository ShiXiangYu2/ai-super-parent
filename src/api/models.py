"""Pydantic 数据模型 — 超级家长 AI"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── 机构 ──
class Institution(BaseModel):
    id: str = Field(default="", description="机构 ID")
    name: str = Field(..., min_length=1, max_length=100, description="机构名称")
    org_type: str = Field(..., description="类型: kindergarten/primary/training")
    region: str = Field(default="", description="所在地区")
    created_at: str = Field(default="", description="创建时间")


# ── 班级 ──
class ClassInfo(BaseModel):
    id: str = Field(default="", description="班级 ID")
    institution_id: str = Field(..., description="所属机构 ID")
    name: str = Field(..., min_length=1, max_length=50, description="班级名称")
    grade: str = Field(default="", description="年级")
    teacher_ids: list[str] = Field(default_factory=list, description="教师 ID 列表")


# ── 教师 ──
class Teacher(BaseModel):
    id: str = Field(default="", description="教师 ID")
    institution_id: str = Field(..., description="所属机构 ID")
    name: str = Field(..., min_length=1, max_length=50, description="教师姓名")
    phone: str = Field(default="", description="手机号")


# ── 学生 ──
class Student(BaseModel):
    id: str = Field(default="", description="学生 ID")
    institution_id: str = Field(..., description="所属机构 ID")
    class_id: str = Field(..., description="班级 ID")
    name: str = Field(..., min_length=1, max_length=50, description="学生姓名")
    birth_date: str = Field(default="", description="出生日期 YYYY-MM-DD")
    gender: str = Field(default="", description="性别: male/female")
    parent_ids: list[str] = Field(default_factory=list, description="关联家长 ID 列表")

    def age_years(self) -> float:
        """计算年龄（岁）。"""
        if not self.birth_date:
            return 0.0
        try:
            bd = datetime.strptime(self.birth_date, "%Y-%m-%d").date()
            today = date.today()
            return (today - bd).days / 365.25
        except (ValueError, TypeError):
            return 0.0


# ── 家长 ──
class Parent(BaseModel):
    id: str = Field(default="", description="家长 ID")
    name: str = Field(..., min_length=1, max_length=50, description="家长姓名")
    phone: str = Field(default="", description="手机号")
    student_ids: list[str] = Field(default_factory=list, description="关联学生 ID 列表")


# ── 育儿问答 ──
class AdviceRequest(BaseModel):
    student_id: str = Field(..., min_length=1, description="学生 ID")
    question: str = Field(..., min_length=2, max_length=1000, description="育儿问题")
    context: str = Field(default="", max_length=500, description="额外上下文")


class AdviceRecord(BaseModel):
    id: str = Field(default="", description="记录 ID")
    institution_id: str = Field(default="", description="机构 ID")
    student_id: str = Field(..., description="学生 ID")
    question: str = Field(..., description="育儿问题")
    answer: str = Field(default="", description="AI 回答")
    child_age: float = Field(default=0.0, description="孩子年龄（岁）")
    created_at: str = Field(default="", description="创建时间")


class AdviceResponse(BaseModel):
    id: str
    answer: str
    child_age: float


# ── 成长报告 ──
class ReportRequest(BaseModel):
    student_id: str = Field(..., min_length=1, description="学生 ID")
    month: str = Field(default="", description="报告月份 YYYY-MM")


class DimensionScore(BaseModel):
    name: str = Field(..., description="维度名称")
    score: float = Field(..., ge=1.0, le=10.0, description="评分 1-10")
    description: str = Field(default="", description="维度描述")


class Report(BaseModel):
    id: str = Field(default="", description="报告 ID")
    student_id: str = Field(..., description="学生 ID")
    institution_id: str = Field(default="", description="机构 ID")
    month: str = Field(..., description="报告月份 YYYY-MM")
    dimensions: list[DimensionScore] = Field(default_factory=list, description="各维度评分")
    summary: str = Field(default="", description="AI 综合评语")
    suggestions: str = Field(default="", description="AI 改善建议")
    created_at: str = Field(default="", description="创建时间")


class ReportResponse(BaseModel):
    reports: list[Report]


# ── 评语辅助 ──
class CommunicationRequest(BaseModel):
    student_id: str = Field(..., min_length=1, description="学生 ID")
    scenario: str = Field(..., description="场景: comment/review/meeting")
    highlights: str = Field(default="", max_length=500, description="教师备注的关键点")
    tone: str = Field(default="warm", description="语气: warm/formal/encouraging")


class CommunicationResponse(BaseModel):
    draft: str


# ── 成长趋势 ──
class TrendPoint(BaseModel):
    month: str
    dimensions: dict[str, float]


class TrendResponse(BaseModel):
    student_id: str
    student_name: str
    trends: list[TrendPoint]


# ── 通用 ──
class ErrorResponse(BaseModel):
    detail: str
