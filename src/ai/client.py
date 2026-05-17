"""LLM AI 客户端 — 封装 OpenAI API 调用"""
import json
import logging
import os
import re
from typing import Optional

logger = logging.getLogger(__name__)

LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")


def _call_llm(prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
    """调用 LLM API。无 API Key 时返回 mock 响应。"""
    if not LLM_API_KEY:
        logger.warning("LLM_API_KEY 未设置，返回 mock 响应")
        return _mock_response(prompt)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=2048,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        logger.error(f"LLM 调用失败: {e}")
        return _mock_response(prompt)


def _mock_response(prompt: str) -> str:
    """无 API Key 时的 mock 回复（用于开发/测试）。"""
    if "评语" in prompt or "评语辅助" in prompt:
        return (
            "【学生姓名】同学，这学期你在各方面都取得了明显的进步。"
            "课堂上认真听讲，积极思考，能够主动回答问题。"
            "在团队合作中表现出良好的沟通能力，和同学们相处融洽。"
            "建议下学期在专注力方面继续加强，培养更持久的学习兴趣。"
            "期待你更大的进步！"
        )
    if "报告" in prompt or "成长报告" in prompt or "发展报告" in prompt:
        dims = {
            "认知能力": 7.5,
            "社交能力": 8.0,
            "情感发展": 7.0,
            "运动能力": 8.5,
            "语言表达": 7.5,
        }
        return json.dumps({
            "dimensions": [{"name": k, "score": v} for k, v in dims.items()],
            "summary": "孩子本月在各维度均有稳步提升，尤其在社交和运动方面表现突出。建议多鼓励孩子表达自己的想法，培养独立思考能力。",
            "suggestions": "1. 每天安排15分钟亲子阅读时间\n2. 多带孩子参加户外集体活动\n3. 鼓励孩子自己整理玩具和物品",
        }, ensure_ascii=False)
    # 默认：育儿问答
    return (
        "根据您孩子的年龄和发展阶段，建议如下：\n\n"
        "1. **建立规律作息**：固定起床、用餐、睡眠时间，帮助孩子建立安全感。\n"
        "2. **多进行亲子对话**：每天至少15分钟专注的亲子交流时间。\n"
        "3. **鼓励探索游戏**：提供适龄的开放式玩具，鼓励自主探索。\n"
        "4. **正面引导**：多使用正面语言描述期望行为，而非单纯禁止。\n\n"
        "每个孩子的发展节奏不同，以上建议请结合孩子的实际情况灵活调整。"
    )


def get_parenting_advice(question: str, child_age: float, context: str = "") -> str:
    """获取育儿建议。"""
    prompt = f"孩子的年龄：{child_age:.1f}岁\n"
    if context:
        prompt += f"额外信息：{context}\n"
    prompt += f"家长的问题：{question}\n"
    prompt += "\n请根据孩子的年龄和发展阶段，给出具体、可操作的育儿建议。要求：\n"
    prompt += "1. 回答要有针对性，贴合该年龄段的特点\n"
    prompt += "2. 给出2-4条具体可操作的建议\n"
    prompt += "3. 语气温暖、鼓励，避免说教\n"
    prompt += "4. 使用中文回答"

    system = "你是一个专业的育儿顾问，拥有儿童发展心理学背景。你的职责是根据孩子的年龄和发展阶段，为家长提供科学、温暖、可操作的育儿建议。"
    return _call_llm(prompt, system, temperature=0.7)


def generate_report(student_name: str, child_age: float, month: str) -> str:
    """生成月度发展报告。"""
    prompt = (
        f"请为{child_age:.1f}岁的学生「{student_name}」生成{month}月度发展报告。\n"
        "请从以下5个维度评估：认知能力、社交能力、情感发展、运动能力、语言表达。\n"
        "请以JSON格式返回，包含：\n"
        '1. "dimensions": 每个维度名称、评分(1-10)、简短描述\n'
        '2. "summary": 综合评语（50-100字）\n'
        '3. "suggestions": 改善建议（分点列出）\n\n'
        "要求：评分要合理分布，综合评语要温暖、有针对性，改善建议要具体可操作。"
    )
    system = "你是一个专业的幼儿教育评估专家。你擅长从多维度观察和评价儿童的发展状况，并能给出科学、温暖的反馈。"
    return _call_llm(prompt, system, temperature=0.5)


def generate_communication_draft(
    student_name: str, child_age: float, scenario: str, highlights: str, tone: str
) -> str:
    """生成家校沟通内容草稿。"""
    tone_desc = {"warm": "温暖亲切", "formal": "正式专业", "encouraging": "鼓励肯定"}
    prompt = (
        f"场景：{scenario}\n"
        f"学生：{student_name}（{child_age:.1f}岁）\n"
        f"教师备注：{highlights}\n"
        f"语气要求：{tone_desc.get(tone, '温暖亲切')}\n\n"
        "请根据以上信息，撰写一段与家长沟通的内容。要求：\n"
        "1. 先肯定孩子的优点和进步\n"
        "2. 如果有关注点，以建设性方式提出\n"
        "3. 给出家长配合建议\n"
        "4. 语言温暖专业，避免过于技术化\n"
        "5. 100-200字"
    )
    system = "你是一个经验丰富的班主任老师，擅长与家长进行有效的家校沟通。你的沟通风格温暖、专业，既能传递信息，又能建立信任。"
    return _call_llm(prompt, system, temperature=0.7)


def extract_json(text: str) -> Optional[dict]:
    """从 LLM 响应中提取 JSON。"""
    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # 尝试从 ```json ... ``` 中提取
    m = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    return None
