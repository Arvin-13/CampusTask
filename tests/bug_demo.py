"""Bug 修复演示 —— 模拟 complete_task 误写成删除任务的场景。"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from task_model import TASK_STATUS_DONE


def complete_task_buggy(task_id, tasks):
    """Bug 版：完成 = 删除（错误实现）"""
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return tasks
    raise LookupError(f"未找到编号为 {task_id} 的任务")


def complete_task_correct(task_id, tasks):
    """正确版：改状态为 done，保留记录"""
    for task in tasks:
        if task["id"] == task_id:
            if task["status"] == "done":
                raise ValueError(f"任务 #{task_id}「{task['title']}」已经完成过了")
            task["status"] = TASK_STATUS_DONE
            return task
    raise LookupError(f"未找到编号为 {task_id} 的任务")


def demo():
    print("=" * 60)
    print("  Bug 修复过程演示")
    print("=" * 60)

    sample = [
        {"id": 1, "title": "完成实验", "status": "pending", "created_at": "2026-06-14 10:00:00"},
        {"id": 2, "title": "复习数学", "status": "pending", "created_at": "2026-06-14 10:01:00"},
    ]

    print("\n[BUG 版] 操作前: 2 个任务")
    result = complete_task_buggy(1, sample.copy())
    print(f"         操作后: {len(result)} 个任务  ← 任务被删除了！")

    print("\n[正确版] 操作前: 2 个任务")
    correct_sample = [t.copy() for t in sample]
    result = complete_task_correct(1, correct_sample)
    print(f"         操作后: {len(correct_sample)} 个任务 (任务 #1 状态: '{result['status']}')  ← 正确")

    print("\n" + "=" * 60)
    print("  以下测试可在 Bug 版中暴露问题：")
    print("=" * 60)
    print("""
  1. test_complete_task_preserves_record_not_deletes_it
     → 断言任务存在，但 bug 版已删除 → FAIL

  2. test_task_persists_after_multiple_operations
     → 断言 len == 2，但 bug 版只剩 1 → FAIL

  3. test_statistics_after_completing_all
     → 断言 total == 2，但 bug 版 total == 0 → FAIL

  修复：tasks.remove(task) → task["status"] = "done"
""")


if __name__ == "__main__":
    demo()
