"""
bug_demo.py —— Bug 修复过程演示脚本

此脚本为独立演示文件，不修改 CampusTask 的任何现有代码。
它模拟了 "complete_task 误写成删除任务" 的 bug 场景。

用法：
  python tests/bug_demo.py      # 演示 bug 版和修复版的对比
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from task_model import TASK_STATUS_DONE


# ═══════════════════════════════════════════════════════════════════════════
# 🐛 Bug 版本：错误地把"完成任务"实现成了"删除任务"
# ═══════════════════════════════════════════════════════════════════════════

def complete_task_BUGGY(task_id: int, tasks: list[dict]) -> list[dict]:
    """❌ Bug 版本：完成任务的逻辑被误写成了删除任务。"""
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)  # 🐛 这里应该改状态，而不是删除！
            return tasks
    raise LookupError(f"未找到编号为 {task_id} 的任务")


# ═══════════════════════════════════════════════════════════════════════════
# ✅ 正确版本
# ═══════════════════════════════════════════════════════════════════════════

def complete_task_CORRECT(task_id: int, tasks: list[dict]) -> dict:
    """✅ 正确版本：将任务状态改为 done，保留记录。"""
    for task in tasks:
        if task["id"] == task_id:
            if task["status"] == "done":
                raise ValueError(f"任务 #{task_id}「{task['title']}」已经完成过了")
            task["status"] = TASK_STATUS_DONE
            return task
    raise LookupError(f"未找到编号为 {task_id} 的任务")


# ═══════════════════════════════════════════════════════════════════════════
# 演示
# ═══════════════════════════════════════════════════════════════════════════

def demonstrate():
    print("=" * 60)
    print("  [BUG] Bug 修复过程演示")
    print("=" * 60)

    sample = [
        {"id": 1, "title": "完成实验", "status": "pending", "created_at": "2026-06-14 10:00:00"},
        {"id": 2, "title": "复习数学", "status": "pending", "created_at": "2026-06-14 10:01:00"},
    ]

    # --- Bug 版本 ---
    print("\n[BUG版] Bug 版本（complete_task 误写成删除）：")
    print(f"   操作前: {len(sample)} 个任务 — {[t['title'] for t in sample]}")
    try:
        result = complete_task_BUGGY(1, sample.copy())
        print(f"   操作后: {len(result)} 个任务 — {[t['title'] for t in result]}")
        print("   [FAIL] 测试失败：任务被删除了！任务数量从 2 变成 1")
    except Exception as e:
        print(f"   异常: {e}")

    # --- 正确版本 ---
    print("\n[正确版] 正确版本（改状态为 done）：")
    correct_sample = [t.copy() for t in sample]
    print(f"   操作前: {len(correct_sample)} 个任务 — {[t['title'] for t in correct_sample]}")
    try:
        result = complete_task_CORRECT(1, correct_sample)
        print(f"   操作后: {len(correct_sample)} 个任务 — {[t['title'] for t in correct_sample]}")
        print(f"   任务 #1 状态: '{result['status']}'")
        print("   [PASS] 测试通过：任务被正确标记为 done，记录保留")
    except Exception as e:
        print(f"   异常: {e}")

    # --- 总结 ---
    print("\n" + "=" * 60)
    print("  [总结] 测试如何捕获这个 Bug")
    print("=" * 60)
    print("""
  以下 3 个测试会在 Bug 版本中失败：

  1. test_complete_task_preserves_record_not_deletes_it
     → 断言任务不为 None，但 bug 版中任务已被删除 → FAIL

  2. test_task_persists_after_multiple_operations
     → 断言 len(all_tasks) == 2，但 bug 版删除后只有 1 个 → FAIL

  3. test_statistics_after_completing_all
     → 断言 total == 2，但 bug 版删除后 total == 0 → FAIL

  修复方法：
    把 tasks.remove(task) 改回 task["status"] = TASK_STATUS_DONE
""")


if __name__ == "__main__":
    demonstrate()
