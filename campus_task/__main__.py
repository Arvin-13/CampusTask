import sys
import argparse
import logging
import csv
from datetime import datetime

sys.path.insert(0, '..')
from task_service import (
    add_task, get_all_tasks, get_pending_tasks, get_done_tasks,
    get_overdue_tasks, get_tasks_by_priority, get_tasks_sorted_by_deadline,
    search_tasks, complete_task, get_statistics,
)

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('campus_task.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

PRIORITY_MARKS = {"high": "🔴", "medium": "🟡", "low": "🟢"}

def cmd_add(args):
    try:
        task = add_task(args.title, args.deadline, args.priority)
        mark = PRIORITY_MARKS.get(task["priority"], "")
        msg = f'已添加 #{task["id"]}：{mark} {task["title"]}'
        if task.get("deadline"):
            msg += f"（截止: {task['deadline']}）"
        print(msg)
    except ValueError as e:
        logging.error(str(e))
        print(f"错误: {e}")

def cmd_list(args):
    pending = get_pending_tasks()
    done = get_done_tasks()

    if not pending and not done:
        print("暂无任务")
        print('   使用: python -m campus_task add "任务标题"')
        return

    print("=" * 50)
    print("  校园任务清单")
    print("=" * 50)

    if pending:
        print(f"\n待完成 ({len(pending)} 项)：")
        print("-" * 40)
        for t in pending:
            p = t.get("priority", "medium")
            mark = PRIORITY_MARKS.get(p, "")
            dl = f"  截止: {t['deadline']}" if t.get("deadline") else ""
            print(f"  [{t['id']}] {mark} {t['title']}{dl}")

    if done:
        print(f"\n已完成 ({len(done)} 项)：")
        print("-" * 40)
        for t in done:
            print(f"  [{t['id']}] {t['title']}")

    stats = get_statistics()
    parts = [f"总计: {stats['total']}", f"待完成: {stats['pending']}", f"已完成: {stats['done']}"]
    if stats.get("overdue", 0) > 0:
        parts.append(f"已过期: {stats['overdue']}")
    print(f"\n>> {' | '.join(parts)}")

def cmd_done(args):
    try:
        task = complete_task(args.id)
        print(f"任务 #{task['id']}「{task['title']}」已完成！")
    except LookupError as e:
        logging.error(str(e))
        print(f"错误: {e}")
    except ValueError as e:
        logging.error(str(e))
        print(f"错误: {e}")

def cmd_export(args):
    tasks = get_all_tasks()
    try:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', '标题', '状态', '优先级', '截止日期', '创建时间'])
            for t in tasks:
                writer.writerow([
                    t['id'],
                    t['title'],
                    '已完成' if t['status'] == 'done' else '待完成',
                    {'high': '高', 'medium': '中', 'low': '低'}.get(t.get('priority'), '中'),
                    t.get('deadline', ''),
                    t.get('created_at', '')
                ])
        print(f"任务已导出到 {args.output}")
    except Exception as e:
        logging.error(f"导出失败: {e}")
        print(f"导出失败: {e}")

def cmd_overdue(args):
    overdue = get_overdue_tasks()
    if not overdue:
        print("没有过期的任务")
        return
    print(f"\n已过期 ({len(overdue)} 项):")
    print("-" * 40)
    for t in overdue:
        print(f"  [{t['id']}] {t['title']}（截止: {t.get('deadline', '?')}）")

def cmd_search(args):
    results = search_tasks(args.keyword)
    if not results:
        print(f"未找到包含关键词 '{args.keyword}' 的任务")
        return
    print(f"\n搜索结果（'{args.keyword}'）:")
    print("-" * 40)
    for t in results:
        status = "✓" if t["status"] == "done" else "○"
        dl = f" 截止: {t['deadline']}" if t.get("deadline") else ""
        print(f"  [{t['id']}] {status} {t['title']}{dl}")

def cmd_priority(args):
    if args.level not in {"high", "medium", "low"}:
        print(f"无效的优先级 '{args.level}'，可选：high / medium / low")
        return
    tasks = get_tasks_by_priority(args.level)
    mark = PRIORITY_MARKS.get(args.level, "")
    print(f"\n{mark} 优先级为 '{args.level}' 的任务 ({len(tasks)} 项):")
    print("-" * 40)
    for t in tasks:
        status = "✓" if t["status"] == "done" else "○"
        print(f"  [{t['id']}] {status} {t['title']}")

def cmd_deadline(args):
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
        print(f"\n待完成 ({len(pending)} 项)：")
        print("-" * 40)
        for t in pending:
            p = t.get("priority", "medium")
            mark = PRIORITY_MARKS.get(p, "")
            dl = f"  截止: {t['deadline']}" if t.get("deadline") else "  无截止日期"
            print(f"  [{t['id']}] {mark} {t['title']}{dl}")

    if done:
        print(f"\n已完成 ({len(done)} 项)：")
        print("-" * 40)
        for t in done:
            print(f"  [{t['id']}] {t['title']}")

def main():
    from campus_task import __version__

    parser = argparse.ArgumentParser(
        prog='campus_task',
        description='校园任务清单 - 命令行任务管理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  python -m campus_task add "复习软件工程"
  python -m campus_task add "复习软件工程" --deadline 2026-06-20 --priority high
  python -m campus_task list
  python -m campus_task done 1
  python -m campus_task export tasks.csv"""
    )
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    add_parser = subparsers.add_parser('add', help='添加新任务')
    add_parser.add_argument('title', help='任务标题')
    add_parser.add_argument('--deadline', help='截止日期 (YYYY-MM-DD)')
    add_parser.add_argument('--priority', choices=['high', 'medium', 'low'], default='medium', help='优先级')
    add_parser.set_defaults(func=cmd_add)

    list_parser = subparsers.add_parser('list', help='列出所有任务')
    list_parser.set_defaults(func=cmd_list)

    done_parser = subparsers.add_parser('done', help='标记任务完成')
    done_parser.add_argument('id', type=int, help='任务编号')
    done_parser.set_defaults(func=cmd_done)

    export_parser = subparsers.add_parser('export', help='导出任务到CSV')
    export_parser.add_argument('output', help='输出文件名')
    export_parser.set_defaults(func=cmd_export)

    overdue_parser = subparsers.add_parser('overdue', help='查看过期任务')
    overdue_parser.set_defaults(func=cmd_overdue)

    search_parser = subparsers.add_parser('search', help='搜索任务')
    search_parser.add_argument('keyword', help='搜索关键词')
    search_parser.set_defaults(func=cmd_search)

    priority_parser = subparsers.add_parser('priority', help='按优先级筛选')
    priority_parser.add_argument('level', choices=['high', 'medium', 'low'], help='优先级级别')
    priority_parser.set_defaults(func=cmd_priority)

    deadline_parser = subparsers.add_parser('deadline', help='按截止日期排序')
    deadline_parser.set_defaults(func=cmd_deadline)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except Exception as e:
        logging.error(f"执行命令 '{args.command}' 时发生错误: {e}", exc_info=True)
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
