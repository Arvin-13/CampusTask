"""任务业务逻辑 —— 在模型层和存储层之间编排操作，向 CLI 暴露业务接口。"""

from __future__ import annotations

from datetime import date

from task_model import (
    create_task, validate_title, validate_deadline, validate_priority,
    TASK_STATUS_DONE, TASK_STATUS_PENDING, PRIORITY_ORDER,
)
from task_storage import load_tasks, save_tasks


def _next_id(tasks: list[dict]) -> int:
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1


def add_task(title: str, deadline: str | None = None,
             priority: str = "medium") -> dict:
    cleaned = title.strip()
    if err := validate_title(cleaned):
        raise ValueError(err)
    if err := validate_deadline(deadline):
        raise ValueError(err)
    if err := validate_priority(priority):
        raise ValueError(err)

    tasks = load_tasks()
    task = create_task(_next_id(tasks), cleaned, deadline, priority)
    tasks.append(task)
    save_tasks(tasks)
    return task


def get_all_tasks() -> list[dict]:
    tasks = load_tasks()
    tasks.sort(key=lambda t: (PRIORITY_ORDER.get(t.get("priority"), 2), t["id"]))
    return tasks


def get_pending_tasks() -> list[dict]:
    return [t for t in get_all_tasks() if t["status"] == TASK_STATUS_PENDING]


def get_done_tasks() -> list[dict]:
    return [t for t in get_all_tasks() if t["status"] == TASK_STATUS_DONE]


def get_tasks_by_priority(priority: str) -> list[dict]:
    return [t for t in get_all_tasks() if t.get("priority") == priority]


def get_task_by_id(task_id: int) -> dict | None:
    for t in get_all_tasks():
        if t["id"] == task_id:
            return t
    return None


def get_overdue_tasks() -> list[dict]:
    today = date.today()
    overdue = []
    for t in get_pending_tasks():
        dl = t.get("deadline")
        if dl is None:
            continue
        try:
            if date.fromisoformat(dl) < today:
                overdue.append(t)
        except (ValueError, TypeError):
            pass
    return overdue


def complete_task(task_id: int) -> dict:
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            if t["status"] == TASK_STATUS_DONE:
                raise ValueError(f"任务 #{task_id}「{t['title']}」已经完成过了")
            t["status"] = TASK_STATUS_DONE
            save_tasks(tasks)
            return t
    raise LookupError(f"未找到编号为 {task_id} 的任务")


def get_statistics() -> dict:
    all_tasks = get_all_tasks()
    pending = [t for t in all_tasks if t["status"] == TASK_STATUS_PENDING]
    done = [t for t in all_tasks if t["status"] == TASK_STATUS_DONE]
    return {
        "total": len(all_tasks),
        "pending": len(pending),
        "done": len(done),
        "overdue": len(get_overdue_tasks()),
    }


def get_tasks_sorted_by_deadline() -> list[dict]:
    tasks = load_tasks()
    tasks.sort(key=lambda t: (t.get("deadline") is None, t.get("deadline", "")))
    return tasks


def search_tasks(keyword: str) -> list[dict]:
    if not keyword or not keyword.strip():
        return []
    kw = keyword.lower().strip()
    return [t for t in get_all_tasks() if kw in t.get("title", "").lower()]
