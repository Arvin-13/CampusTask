"""任务数据持久化 —— JSON 文件读写，屏蔽文件路径、编码和异常处理细节。"""

from __future__ import annotations

import json
import os

TASKS_FILE = "tasks.json"


def load_tasks() -> list[dict]:
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_tasks(tasks: list[dict]) -> None:
    with open(TASKS_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, ensure_ascii=False, indent=2)
