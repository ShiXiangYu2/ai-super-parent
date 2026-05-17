"""种子数据 — 用于开发/演示模式"""
from datetime import datetime, timezone

SEED_INSTITUTIONS = [
    {"id": "inst-001", "name": "阳光幼儿园", "org_type": "kindergarten", "region": "北京市朝阳区", "created_at": datetime.now(timezone.utc).isoformat()},
]

SEED_TEACHERS = [
    {"id": "teacher-001", "institution_id": "inst-001", "name": "张老师", "phone": "13800000001"},
    {"id": "teacher-002", "institution_id": "inst-001", "name": "李老师", "phone": "13800000002"},
]

SEED_CLASSES = [
    {"id": "class-001", "institution_id": "inst-001", "name": "小班(1班)", "grade": "小班", "teacher_ids": ["teacher-001"]},
    {"id": "class-002", "institution_id": "inst-001", "name": "中班(1班)", "grade": "中班", "teacher_ids": ["teacher-002"]},
]

SEED_STUDENTS = [
    {"id": "student-001", "institution_id": "inst-001", "class_id": "class-001", "name": "小明", "birth_date": "2021-03-15", "gender": "male", "parent_ids": ["parent-001"]},
    {"id": "student-002", "institution_id": "inst-001", "class_id": "class-001", "name": "小红", "birth_date": "2021-07-20", "gender": "female", "parent_ids": ["parent-002"]},
    {"id": "student-003", "institution_id": "inst-001", "class_id": "class-002", "name": "小刚", "birth_date": "2020-05-10", "gender": "male", "parent_ids": ["parent-003"]},
]

SEED_PARENTS = [
    {"id": "parent-001", "name": "小明妈妈", "phone": "13900000001", "student_ids": ["student-001"]},
    {"id": "parent-002", "name": "小红爸爸", "phone": "13900000002", "student_ids": ["student-002"]},
    {"id": "parent-003", "name": "小刚妈妈", "phone": "13900000003", "student_ids": ["student-003"]},
]
