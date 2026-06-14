"""
task_service.py —— 任务业务逻辑

职责：实现添加、查询、完成任务等核心业务操作。
它是模型层和存储层之间的"粘合剂"：
  - 从 storage 获取 / 保存数据。
  - 用 model 创建 / 校验任务对象。
  - 向 main 暴露语义清晰的业务接口。

main.py 只与本模块对话，不直接接触 task_storage / task_model。
"""

from task_model import (
    create_task,
    validate_title,
    validate_deadline,
    TASK_STATUS_DONE,
    TASK_STATUS_PENDING,
)
from task_storage import load_tasks, save_tasks


# ---------------------------------------------------------------------------
# 内部工具函数
# ---------------------------------------------------------------------------

def _get_next_id(tasks: list[dict]) -> int:
    """根据现有任务列表计算下一个可用编号。"""
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1


# ---------------------------------------------------------------------------
# 公共业务接口
# ---------------------------------------------------------------------------

def add_task(title: str, deadline: str | None = None) -> dict:
    """添加一个新任务并持久化。

    Args:
        title:    用户输入的任务标题（可含首尾空白，本函数会处理）。
        deadline: 可选的截止日期，格式 YYYY-MM-DD。

    Returns:
        dict: 成功创建的任务记录。

    Raises:
        ValueError: 标题或截止日期校验不通过时抛出。
    """
    cleaned_title = title.strip()
    error = validate_title(cleaned_title)
    if error:
        raise ValueError(error)

    # 校验截止日期（如果提供）
    deadline_error = validate_deadline(deadline)
    if deadline_error:
        raise ValueError(deadline_error)

    tasks = load_tasks()
    new_task = create_task(_get_next_id(tasks), cleaned_title, deadline)
    tasks.append(new_task)
    save_tasks(tasks)
    return new_task


def get_all_tasks() -> list[dict]:
    """获取所有任务（按 id 升序）。"""
    tasks = load_tasks()
    tasks.sort(key=lambda t: t["id"])
    return tasks


def get_pending_tasks() -> list[dict]:
    """获取所有待完成任务。"""
    return [t for t in get_all_tasks() if t["status"] == TASK_STATUS_PENDING]


def get_done_tasks() -> list[dict]:
    """获取所有已完成任务。"""
    return [t for t in get_all_tasks() if t["status"] == TASK_STATUS_DONE]


def get_task_by_id(task_id: int) -> dict | None:
    """按编号查找任务。"""
    for task in get_all_tasks():
        if task["id"] == task_id:
            return task
    return None


def complete_task(task_id: int) -> dict:
    """将指定编号的任务标记为已完成。

    Args:
        task_id: 要完成的任务编号。

    Returns:
        dict: 更新后的任务记录。

    Raises:
        LookupError:   任务不存在。
        ValueError:    任务已经完成。
    """
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            if task["status"] == TASK_STATUS_DONE:
                raise ValueError(f"任务 #{task_id}「{task['title']}」已经完成过了")
            task["status"] = TASK_STATUS_DONE
            save_tasks(tasks)
            return task
    raise LookupError(f"未找到编号为 {task_id} 的任务")


def get_overdue_tasks() -> list[dict]:
    """获取所有已过期的待办任务（当前日期超过 deadline）。"""
    from datetime import date
    today = date.today()
    overdue = []
    for task in get_pending_tasks():
        dl = task.get("deadline")
        if dl is not None:
            try:
                dl_date = date.fromisoformat(dl)
                if dl_date < today:
                    overdue.append(task)
            except (ValueError, TypeError):
                pass  # 忽略格式异常的 deadline
    return overdue


def get_statistics() -> dict:
    """返回任务统计信息。"""
    all_tasks = get_all_tasks()
    pending = [t for t in all_tasks if t["status"] == TASK_STATUS_PENDING]
    done = [t for t in all_tasks if t["status"] == TASK_STATUS_DONE]
    return {
        "total": len(all_tasks),
        "pending": len(pending),
        "done": len(done),
        "overdue": len(get_overdue_tasks()),
    }
