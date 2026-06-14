"""
task_storage.py —— 任务数据持久化

职责：负责与 JSON 文件之间的读写操作，屏蔽文件路径、编码和异常处理细节。
上层（service）只需要调用 load_tasks() / save_tasks()，无需关心文件是否存在、
JSON 是否损坏等底层问题。

设计原则：
  - 只做存储，不做业务判断。
  - 文件不存在 → 返回空列表，不报错。
  - JSON 损坏   → 返回空列表，不崩溃。
"""

import json
import os

# ---------------------------------------------------------------------------
# 文件路径
# ---------------------------------------------------------------------------
TASKS_FILE = "tasks.json"


# ---------------------------------------------------------------------------
# 公共接口
# ---------------------------------------------------------------------------

def load_tasks() -> list[dict]:
    """从 JSON 文件读取所有任务。

    Returns:
        list[dict]: 任务列表。文件不存在或内容损坏时返回空列表。
    """
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, OSError):
        return []


def save_tasks(tasks: list[dict]) -> None:
    """将任务列表写入 JSON 文件。

    Args:
        tasks: 要持久化的任务列表。
    """
    with open(TASKS_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, ensure_ascii=False, indent=2)
