"""任务数据模型 —— 定义数据结构、状态常量、校验规则和工厂函数。"""

from __future__ import annotations

import re
from datetime import datetime

TASK_STATUS_PENDING = "pending"
TASK_STATUS_DONE = "done"

PRIORITY_LOW = "low"
PRIORITY_MEDIUM = "medium"
PRIORITY_HIGH = "high"
PRIORITY_ORDER = {PRIORITY_HIGH: 1, PRIORITY_MEDIUM: 2, PRIORITY_LOW: 3}

TASK_REQUIRED_FIELDS = {
    "id": int,
    "title": str,
    "status": str,
    "created_at": str,
    "deadline": (str, type(None)),
    "priority": str,
}


def create_task(task_id: int, title: str, deadline: str | None = None,
                priority: str = PRIORITY_MEDIUM) -> dict:
    return {
        "id": task_id,
        "title": title,
        "status": TASK_STATUS_PENDING,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "deadline": deadline,
        "priority": priority,
    }


def validate_title(title: str) -> str | None:
    if not title:
        return "任务标题不能为空"
    if len(title) > 200:
        return "任务标题不能超过 200 个字符"
    return None


def validate_deadline(deadline: str | None) -> str | None:
    if deadline is None:
        return None
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", deadline):
        return "截止日期格式错误，应为 YYYY-MM-DD（如 2026-12-31）"
    try:
        datetime.strptime(deadline, "%Y-%m-%d")
    except ValueError:
        return f"不是合法的日期：{deadline}"
    return None


def validate_priority(priority: str) -> str | None:
    if priority not in {PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH}:
        return f"优先级必须是 {PRIORITY_LOW} / {PRIORITY_MEDIUM} / {PRIORITY_HIGH} 之一"
    return None


def is_valid_task(task: dict) -> bool:
    for field, expected_type in TASK_REQUIRED_FIELDS.items():
        if field not in task:
            return False
        if not isinstance(task[field], expected_type):
            return False
    return True
