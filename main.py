"""
main.py —— 命令行交互入口

职责（唯一）：解析命令行参数并将用户意图转发给 task_service，
           然后把 service 返回的结果以可读方式打印出来。

本模块不包含任何文件读写、JSON 处理或业务判断 ——
这些职责分别由 task_storage、task_model 和 task_service 承担。
"""

import sys

# 让 Windows 命令行能正常显示中文
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from task_service import (
    add_task,
    get_all_tasks,
    get_pending_tasks,
    get_done_tasks,
    get_overdue_tasks,
    complete_task,
    get_statistics,
)


# ---------------------------------------------------------------------------
# 帮助信息
# ---------------------------------------------------------------------------

def print_usage() -> None:
    """打印程序用法说明。"""
    print("CampusTask -- 校园任务清单")
    print("=" * 50)
    print("用法:")
    print('  python main.py add "任务标题" [--deadline YYYY-MM-DD]')
    print("  python main.py list")
    print("  python main.py done <编号>")
    print("  python main.py overdue")
    print("=" * 50)


# ---------------------------------------------------------------------------
# 输出渲染（视图层）
# ---------------------------------------------------------------------------

def print_section_header(title: str) -> None:
    """打印带装饰的分节标题。"""
    print(f"\n{title}")
    print("-" * 40)


def print_pending_tasks(tasks: list[dict]) -> None:
    """打印待完成任务列表。"""
    print_section_header(f"待完成 ({len(tasks)} 项)：")
    for task in tasks:
        deadline_str = f"  截止: {task['deadline']}" if task.get("deadline") else ""
        print(f"  [{task['id']}] {task['title']}{deadline_str}")
        print(f"      创建时间: {task['created_at']}")


def print_done_tasks(tasks: list[dict]) -> None:
    """打印已完成任务列表。"""
    print_section_header(f"已完成 ({len(tasks)} 项)：")
    for task in tasks:
        print(f"  [{task['id']}] {task['title']}")


def print_statistics(stats: dict) -> None:
    """打印任务统计摘要。"""
    parts = [
        f"总计: {stats['total']}",
        f"待完成: {stats['pending']}",
        f"已完成: {stats['done']}",
    ]
    if stats.get("overdue", 0) > 0:
        parts.append(f"已过期: {stats['overdue']}")
    print(f"\n>> {' | '.join(parts)}")


# ---------------------------------------------------------------------------
# 命令处理函数
# ---------------------------------------------------------------------------

def handle_add(title: str, deadline: str | None = None) -> None:
    """处理 add 命令：添加新任务并打印结果。"""
    try:
        task = add_task(title, deadline)
        msg = f'已添加 #{task["id"]}：{task["title"]}'
        if task.get("deadline"):
            msg += f"（截止: {task['deadline']}）"
        print(msg)
    except ValueError as exc:
        print(str(exc))


def handle_list() -> None:
    """处理 list 命令：分组显示所有任务及统计信息。"""
    pending = get_pending_tasks()
    done = get_done_tasks()

    if not pending and not done:
        print("暂无任务，加一个吧")
        print('   用法: python main.py add "xxx"')
        return

    print("=" * 50)
    print("  校园任务清单")
    print("=" * 50)

    if pending:
        print_pending_tasks(pending)

    if done:
        print_done_tasks(done)

    print_statistics(get_statistics())


def handle_overdue() -> None:
    """处理 overdue 命令：列出已过期的待办任务。"""
    overdue = get_overdue_tasks()
    if not overdue:
        print("没有过期的任务")
        return
    print(f"\n已过期 ({len(overdue)} 项):")
    print("-" * 40)
    from datetime import date
    today = date.today()
    for task in overdue:
        dl = task.get("deadline", "?")
        print(f"  [{task['id']}] {task['title']}（截止: {dl}）")


def handle_done(task_id_str: str) -> None:
    """处理 done 命令：将指定编号的任务标记为完成。"""
    if not task_id_str.isdigit():
        print(f"'{task_id_str}' 不是有效编号")
        print("   示例: python main.py done 1")
        return

    task_id = int(task_id_str)
    try:
        task = complete_task(task_id)
        print(f"任务 #{task['id']}「{task['title']}」已完成！")
    except LookupError:
        print(f"没找到编号 {task_id} 的任务")
        print("   提示: 用 python main.py list 看看有哪些任务")
    except ValueError as exc:
        print(str(exc))


# ---------------------------------------------------------------------------
# 命令路由
# ---------------------------------------------------------------------------

_COMMAND_HANDLERS = {
    "add":  lambda args: _parse_add_command(args),
    "list": lambda _: handle_list(),
    "done": lambda args: handle_done(args[1]) if len(args) > 1
             else print("done 命令需要任务编号\n"
                         "   示例: python main.py done 1"),
    "overdue": lambda _: handle_overdue(),
}


def _parse_add_command(args: list[str]) -> None:
    """解析 add 命令的参数，支持 --deadline 选项。"""
    if len(args) < 2:
        print("add 命令需要任务标题\n"
              '   示例: python main.py add "做实验"\n'
              '   示例: python main.py add "交报告" --deadline 2026-06-20')
        return

    title = args[1]
    deadline = None

    # 解析 --deadline 选项
    for i, arg in enumerate(args):
        if arg == "--deadline" and i + 1 < len(args):
            deadline = args[i + 1]
            break

    handle_add(title, deadline)


def dispatch(args: list[str]) -> None:
    """根据命令名称分发到对应的处理函数。"""
    if not args:
        print_usage()
        return

    command = args[0].lower()
    handler = _COMMAND_HANDLERS.get(command)

    if handler is None:
        print(f"未知命令 '{command}'")
        print_usage()
    else:
        handler(args)


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

def main() -> None:
    """程序入口点。"""
    dispatch(sys.argv[1:])


if __name__ == "__main__":
    main()
