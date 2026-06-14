"""
task_model.py —— 任务数据模型

职责：定义任务的数据结构、状态常量、字段校验规则和任务创建工厂函数。
本模块不涉及任何文件读写或业务逻辑，只关心"一个任务是什么样子"。
"""

from datetime import datetime

# ---------------------------------------------------------------------------
# 状态常量 —— 避免代码中出现硬编码字符串 "pending" / "done"
# ---------------------------------------------------------------------------
TASK_STATUS_PENDING = "pending"
TASK_STATUS_DONE = "done"

# ---------------------------------------------------------------------------
# 优先级常量（实验4 新增）
# ---------------------------------------------------------------------------
PRIORITY_LOW = "low"
PRIORITY_MEDIUM = "medium"
PRIORITY_HIGH = "high"

PRIORITY_ORDER = {PRIORITY_HIGH: 1, PRIORITY_MEDIUM: 2, PRIORITY_LOW: 3}

# 任务必须包含的字段及类型（用于基本校验）
TASK_REQUIRED_FIELDS = {
    "id": int,
    "title": str,
    "status": str,
    "created_at": str,
    "priority": str,  # low / medium / high
}


# ---------------------------------------------------------------------------
# 工厂函数
# ---------------------------------------------------------------------------

def create_task(task_id: int, title: str, priority: str = PRIORITY_MEDIUM) -> dict:
    """根据编号和标题生成一个新任务字典。

    Args:
        task_id:  任务编号，由 service 层保证唯一且递增。
        title:    用户输入的任务标题，已去除首尾空白。
        priority: 优先级，可选 low / medium / high，默认 medium。

    Returns:
        dict: 包含 id / title / status / created_at / priority 五个字段的任务记录。
    """
    return {
        "id": task_id,
        "title": title,
        "status": TASK_STATUS_PENDING,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "priority": priority,
    }


# ---------------------------------------------------------------------------
# 校验函数
# ---------------------------------------------------------------------------

def validate_title(title: str) -> str | None:
    """校验任务标题是否合法。

    Args:
        title: 去除了首尾空白的标题字符串。

    Returns:
        合法时返回 None，否则返回错误描述字符串。
    """
    if not title:
        return "任务标题不能为空"
    if len(title) > 200:
        return "任务标题不能超过 200 个字符"
    return None


def validate_priority(priority: str) -> str | None:
    """校验优先级是否合法。

    Args:
        priority: 优先级字符串，应为 low / medium / high 之一。

    Returns:
        合法时返回 None，否则返回错误描述字符串。
    """
    valid = {PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH}
    if priority not in valid:
        return f"优先级必须是 {PRIORITY_LOW} / {PRIORITY_MEDIUM} / {PRIORITY_HIGH} 之一"
    return None


def is_valid_task(task: dict) -> bool:
    """检查一个任务字典是否包含所有必需字段且类型正确。"""
    for field, expected_type in TASK_REQUIRED_FIELDS.items():
        if field not in task:
            return False
        if not isinstance(task[field], expected_type):
            return False
    return True
