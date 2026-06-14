"""Write the resolved test_task_service.py"""
import pathlib

content = '''"""
test_task_service.py —— 测试 task_service 模块

测试范围：
  - add_task()         添加任务（正常、空标题、编号递增、deadline、priority）
  - get_all_tasks()    查看全部任务（空列表、有数据、按优先级排序）
  - complete_task()    完成任务（存在、不存在、已完成、重复完成）
  - get_task_by_id()   按 ID 查找
  - get_overdue_tasks() 过期任务检测
  - get_tasks_by_priority() 按优先级筛选
  - get_statistics()   统计信息
  - 数据持久化和一致性
"""

import pytest
from task_service import (
    add_task,
    get_all_tasks,
    get_pending_tasks,
    get_done_tasks,
    get_overdue_tasks,
    get_tasks_by_priority,
    get_task_by_id,
    complete_task,
    get_statistics,
)


# ============================================================================
# 测试 add_task() —— 添加任务
# ============================================================================

class TestAddTask:
    """测试添加任务功能。"""

    def test_add_task_success(self, temp_tasks_file):
        """添加任务成功，返回正确字段。"""
        task = add_task("完成软件工程实验3")
        assert task["id"] == 1
        assert task["title"] == "完成软件工程实验3"
        assert task["status"] == "pending"
        assert "created_at" in task
        assert "deadline" in task
        assert "priority" in task

    def test_add_task_trims_whitespace(self, temp_tasks_file):
        """标题首尾空白应被去除。"""
        task = add_task("  去图书馆  ")
        assert task["title"] == "去图书馆"

    def test_add_empty_title_raises_error(self, temp_tasks_file):
        """添加空标题抛出 ValueError。"""
        with pytest.raises(ValueError, match="不能为空"):
            add_task("")

    def test_add_whitespace_only_title_raises_error(self, temp_tasks_file):
        """纯空白标题也视为空。"""
        with pytest.raises(ValueError):
            add_task("   ")

    def test_add_title_exceeding_200_chars_raises_error(self, temp_tasks_file):
        """超长标题抛出错误。"""
        with pytest.raises(ValueError, match="200"):
            add_task("长" * 201)

    def test_task_id_increments(self, temp_tasks_file):
        """连续添加任务，编号递增且不重复。"""
        task1 = add_task("任务A")
        task2 = add_task("任务B")
        task3 = add_task("任务C")
        assert task1["id"] == 1
        assert task2["id"] == 2
        assert task3["id"] == 3
        assert task1["id"] != task2["id"] != task3["id"]

    def test_add_task_persists_to_file(self, temp_tasks_file):
        """添加任务后数据持久化到 JSON 文件。"""
        add_task("持久化测试")
        tasks = get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "持久化测试"

    # deadline 测试
    def test_add_task_with_deadline(self, temp_tasks_file):
        task = add_task("交报告", deadline="2026-12-31")
        assert task["deadline"] == "2026-12-31"

    def test_add_task_without_deadline(self, temp_tasks_file):
        task = add_task("无截止日期")
        assert task["deadline"] is None

    def test_add_task_with_invalid_deadline_raises_error(self, temp_tasks_file):
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            add_task("格式错误", deadline="2026/12/31")

    def test_add_task_with_nonexistent_date_raises_error(self, temp_tasks_file):
        with pytest.raises(ValueError, match="不是合法的日期"):
            add_task("日期不存在", deadline="2026-02-30")

    # priority 测试
    def test_add_task_with_high_priority(self, temp_tasks_file):
        task = add_task("紧急任务", priority="high")
        assert task["priority"] == "high"

    def test_add_task_default_priority_is_medium(self, temp_tasks_file):
        task = add_task("普通任务")
        assert task["priority"] == "medium"

    def test_add_task_with_invalid_priority_raises_error(self, temp_tasks_file):
        with pytest.raises(ValueError):
            add_task("测试", priority="urgent")

    def test_add_task_with_both_deadline_and_priority(self, temp_tasks_file):
        task = add_task("完整任务", deadline="2026-12-31", priority="high")
        assert task["deadline"] == "2026-12-31"
        assert task["priority"] == "high"


# ============================================================================
# 测试查询功能
# ============================================================================

class TestQueryTasks:
    """测试查询任务功能。"""

    def test_get_all_tasks_empty(self, temp_tasks_file):
        tasks = get_all_tasks()
        assert tasks == []
        assert isinstance(tasks, list)

    def test_get_all_tasks_sorted_by_priority(self, temp_tasks_file):
        add_task("低优先", priority="low")
        add_task("高优先", priority="high")
        add_task("中优先", priority="medium")
        tasks = get_all_tasks()
        priorities = [t.get("priority") for t in tasks]
        assert priorities[0] == "high"
        assert len(tasks) == 3

    def test_get_pending_tasks_only_returns_pending(self, temp_tasks_file_with_data):
        pending = get_pending_tasks()
        assert all(t["status"] == "pending" for t in pending)
        assert len(pending) == 2

    def test_get_done_tasks_only_returns_done(self, temp_tasks_file_with_data):
        done = get_done_tasks()
        assert all(t["status"] == "done" for t in done)
        assert len(done) == 1

    def test_get_task_by_id_exists(self, temp_tasks_file_with_data):
        task = get_task_by_id(2)
        assert task is not None
        assert task["title"] == "复习高等数学"

    def test_get_task_by_id_not_exists(self, temp_tasks_file_with_data):
        task = get_task_by_id(999)
        assert task is None


# ============================================================================
# 测试过期任务检测
# ============================================================================

class TestOverdueTasks:

    def test_overdue_tasks_detected(self, temp_tasks_file):
        add_task("昨天截止", deadline="2020-01-01")
        add_task("未来截止", deadline="2099-12-31")
        overdue = get_overdue_tasks()
        assert len(overdue) == 1
        assert overdue[0]["title"] == "昨天截止"

    def test_no_overdue_when_all_future(self, temp_tasks_file):
        add_task("未来任务", deadline="2099-12-31")
        assert get_overdue_tasks() == []

    def test_overdue_tasks_excludes_done(self, temp_tasks_file):
        add_task("过期但已完成", deadline="2020-01-01")
        complete_task(1)
        assert len(get_overdue_tasks()) == 0

    def test_overdue_from_sample_data(self, temp_tasks_file_with_data):
        overdue = get_overdue_tasks()
        assert any(t["id"] == 3 for t in overdue)


# ============================================================================
# 测试按优先级筛选
# ============================================================================

class TestPriorityFiltering:

    def test_filter_high_priority(self, temp_tasks_file_with_data):
        tasks = get_tasks_by_priority("high")
        assert len(tasks) >= 1
        assert all(t["priority"] == "high" for t in tasks)


# ============================================================================
# 测试 complete_task() —— 完成任务
# ============================================================================

class TestCompleteTask:
    """测试完成任务功能。"""

    def test_complete_existing_task(self, temp_tasks_file_with_data):
        task = complete_task(1)
        assert task["id"] == 1
        assert task["status"] == "done"

    def test_complete_nonexistent_task_raises_error(self, temp_tasks_file_with_data):
        with pytest.raises(LookupError, match="未找到"):
            complete_task(999)

    def test_complete_already_done_task_raises_error(self, temp_tasks_file_with_data):
        with pytest.raises(ValueError, match="已经完成"):
            complete_task(2)

    def test_complete_task_second_time_fails(self, temp_tasks_file):
        add_task("测试重复完成")
        complete_task(1)
        with pytest.raises(ValueError, match="已经完成"):
            complete_task(1)

    def test_complete_task_changes_status_in_storage(self, temp_tasks_file):
        add_task("临时任务")
        complete_task(1)
        task = get_task_by_id(1)
        assert task["status"] == "done"


# ============================================================================
# 测试统计功能
# ============================================================================

class TestStatistics:
    """测试统计信息功能。"""

    def test_statistics_empty(self, temp_tasks_file):
        stats = get_statistics()
        assert stats["total"] == 0
        assert stats["pending"] == 0
        assert stats["done"] == 0
        assert stats["overdue"] == 0

    def test_statistics_with_data(self, temp_tasks_file_with_data):
        stats = get_statistics()
        assert stats["total"] == 3
        assert stats["pending"] == 2
        assert stats["done"] == 1

    def test_statistics_after_completing_all(self, temp_tasks_file):
        add_task("任务1")
        add_task("任务2")
        complete_task(1)
        complete_task(2)
        stats = get_statistics()
        assert stats["total"] == 2
        assert stats["pending"] == 0
        assert stats["done"] == 2


# ============================================================================
# 测试数据一致性（跨模块）
# ============================================================================

class TestDataConsistency:
    """测试跨操作的数据一致性。"""

    def test_task_persists_after_multiple_operations(self, temp_tasks_file):
        add_task("任务A")
        add_task("任务B")
        complete_task(1)
        all_tasks = get_all_tasks()
        assert len(all_tasks) == 2

    def test_id_continues_after_data_load(self, temp_tasks_file_with_data):
        task = add_task("新任务")
        assert task["id"] == 4

    def test_complete_task_preserves_record_not_deletes_it(self, temp_tasks_file):
        add_task("不应被删除的任务")
        complete_task(1)
        task = get_task_by_id(1)
        assert task is not None, "BUG: 任务被删除了！"
        assert task["status"] == "done"
        all_tasks = get_all_tasks()
        assert len(all_tasks) == 1
'''

pathlib.Path('tests/test_task_service.py').write_text(content, encoding='utf-8')
print('test_task_service.py written')
