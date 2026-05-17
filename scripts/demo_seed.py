"""Demo 数据生成 — 超级家长 AI 产品演示场景"""
import json
import logging
import os
import sys
import time
from pathlib import Path

# 确保能找到 src
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.database import (
    create_class, create_student, create_tenant, create_user, get_db,
    init_db, save_advice, save_report, verify_password, hash_password,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("demo-seed")

DEMO_TENANTS = [
    {
        "name": "阳光幼儿园",
        "org_type": "kindergarten",
        "region": "北京市朝阳区",
        "contact_name": "王园长",
        "contact_phone": "13800000001",
        "classes": [
            {
                "name": "小班(1班)", "grade": "小班",
                "students": [
                    ("小明", "2021-03-15", "male"),
                    ("小红", "2021-07-20", "female"),
                    ("小刚", "2021-05-10", "male"),
                    ("小丽", "2021-09-01", "female"),
                    ("小强", "2021-11-12", "male"),
                ],
            },
            {
                "name": "中班(1班)", "grade": "中班",
                "students": [
                    ("朵朵", "2020-03-20", "female"),
                    ("乐乐", "2020-06-15", "male"),
                    ("欣欣", "2020-08-08", "female"),
                    ("浩浩", "2020-02-28", "male"),
                ],
            },
            {
                "name": "大班(1班)", "grade": "大班",
                "students": [
                    ("果果", "2019-04-10", "female"),
                    ("豆豆", "2019-07-22", "male"),
                    ("萌萌", "2019-01-05", "female"),
                ],
            },
        ],
        "parents": [
            ("小明妈妈", "parent@demo.com", "parent123"),
            ("小红爸爸", "parent2@demo.com", "parent123"),
        ],
    },
    {
        "name": "智慧实验小学",
        "org_type": "primary",
        "region": "上海市浦东新区",
        "contact_name": "李校长",
        "contact_phone": "13900000002",
        "classes": [
            {
                "name": "一年级(1班)", "grade": "一年级",
                "students": [
                    ("小华", "2018-03-15", "male"),
                    ("小美", "2018-07-20", "female"),
                ],
            },
        ],
        "parents": [
            ("小华妈妈", "parent3@demo.com", "parent123"),
        ],
    },
]


def generate_sample_reports():
    """生成模拟月度报告数据"""
    dimensions_pool = [
        {"name": "认知能力", "description": "观察力、记忆力、逻辑思维"},
        {"name": "语言发展", "description": "表达能力、词汇量、沟通意愿"},
        {"name": "社交情感", "description": "同伴关系、情绪管理、分享意识"},
        {"name": "身体运动", "description": "大运动、精细动作、协调能力"},
        {"name": "艺术素养", "description": "绘画、音乐、创造力表现"},
    ]
    import random
    months = ["2026-01", "2026-02", "2026-03"]
    scenarios = [
        {
            "summary": "本月孩子在课堂参与度有明显提升，能够主动举手回答问题。与同伴的互动更加积极，乐于分享玩具和想法。在语言表达方面进步显著，能够完整描述日常经历。",
            "suggestions": "建议在家多鼓励孩子讲故事，培养逻辑表达能力。增加亲子阅读时间，每天15-20分钟为宜。多带孩子参加户外活动，锻炼大运动能力。",
        },
        {
            "summary": "孩子在数学逻辑方面展现出浓厚兴趣，能够完成10以内的加减法。社交能力持续进步，在小组活动中能主动承担任务。精细动作发展良好，绘画和手工有明显进步。",
            "suggestions": "可以适当引入益智类桌游，培养策略思维和规则意识。继续鼓励户外运动，建议每周至少3次户外活动时间。",
        },
        {
            "summary": "本学期综合表现优秀。孩子在各维度均有稳定进步，尤其在语言表达和社交能力方面表现突出。能够独立完成日常自理任务，责任感和自律性增强。",
            "suggestions": "暑期建议保持规律的作息时间，可以安排一些兴趣探索活动（音乐、绘画、运动等），为新学期做好准备。",
        },
    ]
    results = []
    for i, month in enumerate(months):
        s = scenarios[i % len(scenarios)]
        dims = []
        for d in dimensions_pool:
            score = round(random.uniform(6.5, 9.5), 1)
            dims.append({"name": d["name"], "score": score, "description": d["description"]})
        results.append({"month": month, "dimensions": dims, "summary": s["summary"], "suggestions": s["suggestions"]})
    return results


def generate_sample_advice():
    """生成模拟育儿问答记录"""
    return [
        ("孩子不爱吃饭怎么办？", "建议从以下几个方面尝试：1) 建立固定的就餐时间和规则，避免餐前零食；2) 让参与简单的食物准备，增加对食物的兴趣；3) 采用\"一口规则\"，鼓励尝试新食物但不强迫；4) 减少就餐时的干扰（电视、iPad等）；5) 以身作则，家长展示良好的饮食习惯。每个孩子的情况不同，建议观察记录找到最适合的方式。"),
        ("孩子总爱发脾气怎么引导？", "情绪管理是幼儿期的重要发展任务。建议：1) 接纳孩子的情绪，帮助他命名感受（\"你生气是因为...\"）；2) 设立清晰的行为界限，但保持温和的态度；3) 教给孩子简单的情绪调节方法，如深呼吸、数数；4) 在情绪平静后一起回顾事件，讨论更好的处理方式；5) 保证充足的睡眠和规律的生活节奏，疲劳和饥饿是情绪爆发的常见诱因。"),
        ("如何培养孩子的阅读习惯？", "培养阅读习惯是一个循序渐进的过程：1) 创设阅读环境——在家中设置舒适的阅读角，书籍放在孩子随手可得的地方；2) 坚持每日亲子阅读15-20分钟，让阅读成为习惯而任务；3) 让孩子自主选择感兴趣的书籍，尊重阅读偏好；4) 阅读后进行简单讨论，提问\"你最喜欢哪个部分？\"，培养理解力；5) 家长做好榜样，让孩子看到你在阅读。坚持21天，阅读习惯就能初步形成。"),
    ]


def seed():
    """一键生成完整 Demo 数据"""
    init_db()

    with get_db() as db:
        existing = db.execute("SELECT COUNT(*) as c FROM tenants").fetchone()
        if existing and existing["c"] > 0:
            log.info("⚠️  数据库已有数据，跳过种子数据生成")
            log.info("   如需重新生成，请删除 data/app.db 后重试")
            return

    parent_idx = 0
    all_parents = []

    for tenant_cfg in DEMO_TENANTS:
        log.info(f"\n{'='*50}")
        log.info(f"🏫 创建机构: {tenant_cfg['name']}")
        tenant = create_tenant(
            tenant_cfg["name"],
            tenant_cfg["org_type"],
            tenant_cfg["region"],
            tenant_cfg["contact_name"],
            tenant_cfg["contact_phone"],
        )
        tid = tenant["id"]

        # 创建管理员
        admin_email = f"admin@{tenant_cfg['name']}.com"
        create_user(tid, tenant_cfg["contact_name"], admin_email, "admin123", "tenant_admin")
        log.info(f"  👤 管理员: {admin_email} / admin123")

        # 创建教师
        teacher_names = ["张老师", "李老师", "王老师"]
        teachers = []
        for i, tname in enumerate(teacher_names[:len(tenant_cfg["classes"])]):
            t = create_user(tid, tname, f"{tname}@{tenant_cfg['name']}.com", "teacher123", "teacher")
            teachers.append(t)
            log.info(f"  👨‍🏫 教师: {tname}")

        # 创建家长
        local_parents = []
        for pname, pemail, ppw in tenant_cfg.get("parents", []):
            p = create_user(tid, pname, pemail, ppw, "parent")
            local_parents.append(p)
            all_parents.append(p)
            log.info(f"  👪 家长: {pname} ({pemail})")

        # 创建班级和学生
        reports_data = generate_sample_reports()
        advice_data = generate_sample_advice()
        all_students = []

        for ci, cls_cfg in enumerate(tenant_cfg["classes"]):
            teacher = teachers[ci] if ci < len(teachers) else teachers[0]
            cls = create_class(tid, cls_cfg["name"], cls_cfg["grade"], [teacher["id"]])
            log.info(f"\n  📚 班级: {cls_cfg['name']} (教师: {teacher['name']})")

            for si, (sname, sbirth, sgender) in enumerate(cls_cfg["students"]):
                parent = local_parents[si % len(local_parents)] if local_parents else None
                parent_id = parent["id"] if parent else ""
                student = create_student(tid, cls["id"], sname, sbirth, sgender, parent_id)
                all_students.append(student)
                log.info(f"    🧒 {sname} ({sbirth}) → 家长: {parent['name'] if parent else '无'}")

                # 为每个学生生成月度报告
                for ri, r in enumerate(reports_data):
                    save_report(
                        tid, student["id"], r["month"],
                        r["dimensions"], r["summary"], r["suggestions"],
                    )
                log.info(f"      📊 已生成 {len(reports_data)} 份月度报告")

                # 为部分学生生成咨询记录
                if si < len(advice_data) and parent:
                    q, a = advice_data[si]
                    save_advice(tid, student["id"], parent["id"], q, a, 3.5)
                    log.info(f"      💬 已生成 AI 育儿问答")

    # 创建超级管理员（平台级）
    log.info(f"\n{'='*50}")
    log.info(f"🔑 创建平台超级管理员")
    first_tenant_id = DEMO_TENANTS[0]["name"]
    with get_db() as db:
        first_tenant = db.execute("SELECT id FROM tenants LIMIT 1").fetchone()
    if first_tenant:
        create_user(first_tenant["id"], "平台管理员", "admin@demo.com", "admin123", "super_admin")
        log.info(f"  👑 平台管理员: admin@demo.com / admin123")
        # 创建标准 Demo 教师账号
        create_user(first_tenant["id"], "张老师", "teacher@demo.com", "teacher123", "teacher")
        log.info(f"  👨‍🏫 标准教师: teacher@demo.com / teacher123")

    log.info(f"\n{'='*50}")
    log.info(f"✅ Demo 数据初始化完成!")
    log.info(f"\n📋 演示账号:")
    log.info(f"  👑 平台管理员: admin@demo.com / admin123")
    log.info(f"  👨‍🏫 教师: teacher@demo.com / teacher123 (也可用 张老师@阳光幼儿园.com 等)")
    log.info(f"  👪 家长1: parent@demo.com / parent123")
    log.info(f"  👪 家长2: parent2@demo.com / parent123")
    log.info(f"  👪 家长3: parent3@demo.com / parent123")
    log.info(f"\n🚀 启动命令: uvicorn src.api.main:app --reload --port 8000")
    log.info(f"🌐 访问地址: http://localhost:8000")


if __name__ == "__main__":
    seed()
