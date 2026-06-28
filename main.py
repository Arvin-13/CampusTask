"""CampusTask —— 命令行校园任务管理工具"""

import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from task_service import (
    add_task, get_all_tasks, get_pending_tasks, get_done_tasks,
    get_overdue_tasks, get_tasks_by_priority, get_tasks_sorted_by_deadline,
    search_tasks, complete_task, get_statistics,
)

PRIORITY_MARKS = {"high": "🔴", "medium": "🟡", "low": "🟢"}


def print_usage():
    print("CampusTask -- 校园任务清单")
    print("=" * 50)
    print("用法:")
    print('  python main.py add "任务标题" [--deadline YYYY-MM-DD] [--priority high|medium|low]')
    print("  python main.py list")
    print("  python main.py done <编号>")
    print("  python main.py overdue")
    print("  python main.py priority <high|medium|low>")
    print("  python main.py deadline")
    print('  python main.py search "关键词"')
    print("=" * 50)


def _section(title):
    print(f"\n{title}")
    print("-" * 40)


def handle_add(title, deadline=None, priority="medium"):
    try:
        task = add_task(title, deadline, priority)
        mark = PRIORITY_MARKS.get(priority, "")
        msg = f'已添加 #{task["id"]}：{mark} {task["title"]}'
        if task.get("deadline"):
            msg += f"（截止: {task['deadline']}）"
        print(msg)
    except ValueError as exc:
        print(str(exc))


def handle_list():
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
        _section(f"待完成 ({len(pending)} 项)：")
        for t in pending:
            p = t.get("priority", "medium")
            mark = PRIORITY_MARKS.get(p, "")
            dl = f"  截止: {t['deadline']}" if t.get("deadline") else ""
            print(f"  [{t['id']}] {mark} {t['title']}{dl}")
            print(f"      创建时间: {t['created_at']}")

    if done:
        _section(f"已完成 ({len(done)} 项)：")
        for t in done:
            print(f"  [{t['id']}] {t['title']}")

    stats = get_statistics()
    parts = [
        f"总计: {stats['total']}",
        f"待完成: {stats['pending']}",
        f"已完成: {stats['done']}",
    ]
    if stats.get("overdue", 0) > 0:
        parts.append(f"已过期: {stats['overdue']}")
    print(f"\n>> {' | '.join(parts)}")


def handle_overdue():
    overdue = get_overdue_tasks()
    if not overdue:
        print("没有过期的任务")
        return
    print(f"\n已过期 ({len(overdue)} 项):")
    print("-" * 40)
    for t in overdue:
        print(f"  [{t['id']}] {t['title']}（截止: {t.get('deadline', '?')}）")


def handle_priority(level):
    if level not in {"high", "medium", "low"}:
        print(f"无效的优先级 '{level}'，可选：high / medium / low")
        return
    tasks = get_tasks_by_priority(level)
    mark = PRIORITY_MARKS.get(level, "")
    print(f"\n{mark} 优先级为 '{level}' 的任务 ({len(tasks)} 项):")
    print("-" * 40)
    for t in tasks:
        status = "✓" if t["status"] == "done" else "○"
        print(f"  [{t['id']}] {status} {t['title']}")


def handle_deadline():
    tasks = get_tasks_sorted_by_deadline()
    if not tasks:
        print("暂无任务")
        return

    print("=" * 50)
    print("  按截止日期排序")
    print("=" * 50)

    pending = [t for t in tasks if t["status"] == "pending"]
    done = [t for t in tasks if t["status"] == "done"]

    if pending:
        _section(f"待完成 ({len(pending)} 项)：")
        for t in pending:
            p = t.get("priority", "medium")
            mark = PRIORITY_MARKS.get(p, "")
            dl = f"  截止: {t['deadline']}" if t.get("deadline") else "  无截止日期"
            print(f"  [{t['id']}] {mark} {t['title']}{dl}")

    if done:
        _section(f"已完成 ({len(done)} 项)：")
        for t in done:
            print(f"  [{t['id']}] {t['title']}")


def handle_search(keyword):
    if not keyword or not keyword.strip():
        print("搜索关键词不能为空")
        print('   示例: python main.py search "报告"')
        return

    results = search_tasks(keyword)
    if not results:
        print(f"未找到包含关键词 '{keyword}' 的任务")
        return

    print(f"\n搜索结果（'{keyword}'）:")
    print("-" * 40)
    for t in results:
        status = "✓" if t["status"] == "done" else "○"
        dl = f" 截止: {t['deadline']}" if t.get("deadline") else ""
        print(f"  [{t['id']}] {status} {t['title']}{dl}")


def handle_done(task_id_str):
    if not task_id_str.isdigit():
        print(f"'{task_id_str}' 不是有效编号")
        print("   示例: python main.py done 1")
        return

    try:
        task = complete_task(int(task_id_str))
        print(f"任务 #{task['id']}「{task['title']}」已完成！")
    except LookupError:
        print(f"没找到编号 {task_id_str} 的任务")
        print("   提示: 用 python main.py list 看看有哪些任务")
    except ValueError as exc:
        print(str(exc))


def _parse_add(args):
    if len(args) < 2:
        print("add 命令需要任务标题\n"
              '   示例: python main.py add "做实验"\n'
              '   示例: python main.py add "交报告" --deadline 2026-06-20 --priority high')
        return

    title = args[1]
    deadline = None
    priority = "medium"

    for i, arg in enumerate(args):
        if arg == "--deadline" and i + 1 < len(args):
            deadline = args[i + 1]
        if arg == "--priority" and i + 1 < len(args):
            priority = args[i + 1]

    handle_add(title, deadline, priority)


_HANDLERS = {
    "add": lambda a: _parse_add(a),
    "list": lambda _: handle_list(),
    "done": lambda a: handle_done(a[1]) if len(a) > 1
             else print("done 命令需要任务编号\n"
                         "   示例: python main.py done 1"),
    "overdue": lambda _: handle_overdue(),
    "priority": lambda a: handle_priority(a[1]) if len(a) > 1
                 else print("priority 命令需要优先级参数\n"
                            "   示例: python main.py priority high"),
    "deadline": lambda _: handle_deadline(),
    "search": lambda a: handle_search(a[1]) if len(a) > 1
              else print("search 命令需要关键词参数\n"
                         '   示例: python main.py search "报告"'),
}


def dispatch(args):
    if not args:
        print_usage()
        return
    command = args[0].lower()
    handler = _HANDLERS.get(command)
    if handler is None:
        print(f"未知命令 '{command}'")
        print_usage()
    else:
        handler(args)


def main():
    dispatch(sys.argv[1:])


if __name__ == "__main__":
    main()
