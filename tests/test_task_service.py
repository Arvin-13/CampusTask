"""
test_task_service.py —— 测试 task_service 模块

测试范围：
  - add_task()         添加任务（正常、空标题、编号递增）
  - get_all_tasks()    查看全部任务（空列表、有数据）
  - complete_task()    完成任务（存在、不存在、已完成、重复完成）
  - get_task_by_id()   按 ID 查找
  - get_statistics()   统计信息
  - 数据持久化和一致性
"""

import pytest
from task_service import (
    add_task,
    get_all_tasks,
    get_pending_tasks,
    get_done_tasks,
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
        """【测试用例1/12】添加任务成功，返回正确字段。"""
        task = add_task("完成软件工程实验3")

        assert task["id"] == 1
        assert task["title"] == "完成软件工程实验3"
        assert task["status"] == "pending"
        assert "created_at" in task

    def test_add_task_trims_whitespace(self, temp_tasks_file):
        """【边界】标题首尾空白应被去除。"""
        task = add_task("  去图书馆  ")

        assert task["title"] == "去图书馆"

    def test_add_empty_title_raises_error(self, temp_tasks_file):
        """【测试用例2/12】添加空标题抛出 ValueError。"""
        with pytest.raises(ValueError, match="不能为空"):
            add_task("")

    def test_add_whitespace_only_title_raises_error(self, temp_tasks_file):
        """【边界】纯空白标题也视为空。"""
        with pytest.raises(ValueError):
            add_task("   ")

    def test_add_title_exceeding_200_chars_raises_error(self, temp_tasks_file):
        """【边界】超长标题抛出错误。"""
        with pytest.raises(ValueError, match="200"):
            add_task("长" * 201)

    def test_task_id_increments(self, temp_tasks_file):
        """【测试用例6/12】连续添加任务，编号递增且不重复。"""
        task1 = add_task("任务A")
        task2 = add_task("任务B")
        task3 = add_task("任务C")

        assert task1["id"] == 1
        assert task2["id"] == 2
        assert task3["id"] == 3
        assert task1["id"] != task2["id"] != task3["id"]

    def test_add_task_persists_to_file(self, temp_tasks_file):
        """【正常】添加任务后数据持久化到 JSON 文件。"""
        add_task("持久化测试")
        tasks = get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "持久化测试"

    # =====================================================================
    # priority 相关测试（实验4 新增）
    # =====================================================================

    def test_add_task_with_high_priority(self, temp_tasks_file):
        """【正常】添加高优先级任务。"""
        task = add_task("紧急任务", priority="high")
        assert task["priority"] == "high"

    def test_add_task_default_priority_is_medium(self, temp_tasks_file):
        """【正常】不指定优先级时默认为 medium。"""
        task = add_task("普通任务")
        assert task["priority"] == "medium"

    def test_add_task_with_invalid_priority_raises_error(self, temp_tasks_file):
        """【失败】非法优先级抛出 ValueError。"""
        with pytest.raises(ValueError):
            add_task("测试", priority="urgent")


# ============================================================================
# 测试查询功能
# ============================================================================

class TestQueryTasks:
    """测试查询任务功能。"""

    def test_get_all_tasks_empty(self, temp_tasks_file):
        """【测试用例3/12】无任务时返回空列表。"""
        tasks = get_all_tasks()
        assert tasks == []
        assert isinstance(tasks, list)

    def test_get_all_tasks_sorted_by_id(self, temp_tasks_file):
        """【正常】返回的任务按 ID 升序排列。"""
        add_task("C")
        add_task("A")
        add_task("B")

        tasks = get_all_tasks()
        ids = [t["id"] for t in tasks]
        assert ids == [1, 2, 3]

    def test_get_pending_tasks_only_returns_pending(self, temp_tasks_file_with_data):
        """【正常】get_pending_tasks 只返回待完成任务。"""
        pending = get_pending_tasks()
        assert all(t["status"] == "pending" for t in pending)
        assert len(pending) == 2  # id=1 和 id=3 是 pending

    def test_get_done_tasks_only_returns_done(self, temp_tasks_file_with_data):
        """【正常】get_done_tasks 只返回已完成任务。"""
        done = get_done_tasks()
        assert all(t["status"] == "done" for t in done)
        assert len(done) == 1  # 只有 id=2 是 done

    def test_get_task_by_id_exists(self, temp_tasks_file_with_data):
        """【正常】按有效 ID 查找返回对应任务。"""
        task = get_task_by_id(2)
        assert task is not None
        assert task["title"] == "复习高等数学"

    def test_get_task_by_id_not_exists(self, temp_tasks_file_with_data):
        """【正常】按不存在的 ID 查找返回 None。"""
        task = get_task_by_id(999)
        assert task is None


# ============================================================================
# 测试 complete_task() —— 完成任务
# ============================================================================

class TestCompleteTask:
    """测试完成任务功能。"""

    def test_complete_existing_task(self, temp_tasks_file_with_data):
        """【测试用例4/12】完成一个存在的待办任务成功。"""
        task = complete_task(1)

        assert task["id"] == 1
        assert task["status"] == "done"

    def test_complete_nonexistent_task_raises_error(self, temp_tasks_file_with_data):
        """【测试用例5/12】完成不存在的任务抛出 LookupError。"""
        with pytest.raises(LookupError, match="未找到"):
            complete_task(999)

    def test_complete_already_done_task_raises_error(self, temp_tasks_file_with_data):
        """【测试用例9/12】重复完成已完成的任務抛出 ValueError。"""
        # 任务 #2 已经是 done 状态
        with pytest.raises(ValueError, match="已经完成"):
            complete_task(2)

    def test_complete_task_second_time_fails(self, temp_tasks_file):
        """【测试用例9补充】刚完成的任务不能再次完成。"""
        add_task("测试重复完成")
        complete_task(1)

        with pytest.raises(ValueError, match="已经完成"):
            complete_task(1)

    def test_complete_task_changes_status_in_storage(self, temp_tasks_file):
        """【正常】完成任务后状态变更被持久化。"""
        add_task("临时任务")
        complete_task(1)

        # 重新加载并验证
        task = get_task_by_id(1)
        assert task["status"] == "done"


# ============================================================================
# 测试统计功能
# ============================================================================

class TestStatistics:
    """测试统计信息功能。"""

    def test_statistics_empty(self, temp_tasks_file):
        """【边界】空任务列表的统计信息。"""
        stats = get_statistics()
        assert stats == {"total": 0, "pending": 0, "done": 0}

    def test_statistics_with_data(self, temp_tasks_file_with_data):
        """【正常】有任务时的统计信息。"""
        stats = get_statistics()
        assert stats["total"] == 3
        assert stats["pending"] == 2
        assert stats["done"] == 1

    def test_statistics_after_completing_all(self, temp_tasks_file):
        """【正常】完成所有任务后统计更新。"""
        add_task("任务1")
        add_task("任务2")
        complete_task(1)
        complete_task(2)

        stats = get_statistics()
        assert stats["total"] == 2
        assert stats["pending"] == 0
        assert stats["done"] == 2


# ============================================================================
# 测试按优先级筛选（实验4 新增）
# ============================================================================

class TestPriorityFiltering:
    """测试 get_tasks_by_priority() 和优先级排序。"""

    def test_filter_high_priority(self, temp_tasks_file_with_data):
        """【正常】筛选高优先级任务。"""
        tasks = get_tasks_by_priority("high")
        assert len(tasks) >= 1
        assert all(t["priority"] == "high" for t in tasks)

    def test_sorted_by_priority_desc(self, temp_tasks_file):
        """【正常】任务列表按优先级降序排列（高→中→低）。"""
        add_task("低优先", priority="low")
        add_task("高优先", priority="high")
        add_task("中优先", priority="medium")

        all_tasks = get_all_tasks()
        priorities = [t.get("priority") for t in all_tasks]
        # 高优先级的应该排在最前面
        assert priorities[0] == "high"


# ============================================================================
# 测试数据一致性（跨模块）
# ============================================================================

class TestDataConsistency:
    """测试跨操作的数据一致性。"""

    def test_task_persists_after_multiple_operations(self, temp_tasks_file):
        """【测试用例10/12】多次操作后数据保持一致。"""
        # 添加
        add_task("任务A")
        add_task("任务B")
        # 完成
        complete_task(1)

        # 验证
        all_tasks = get_all_tasks()
        assert len(all_tasks) == 2
        assert all_tasks[0]["status"] == "done"
        assert all_tasks[1]["status"] == "pending"

    def test_id_continues_after_data_load(self, temp_tasks_file_with_data):
        """【测试用例6补充】从已有数据加载后，新任务编号从最大值+1开始。"""
        task = add_task("新任务")
        assert task["id"] == 4  # 已有 1,2,3

    # =====================================================================
    # 🐛 故意 Bug 演示区域（见实验文档「Bug 修复过程」章节）
    # =====================================================================
    #
    # 以下测试设计用于暴露一个故意的 bug。
    # 详细说明见 实验3-测试文档.md 的"Bug 修复过程"章节。
    #
    # 你可以通过临时修改 task_service.py 中 complete_task() 的实现：
    #   把 task["status"] = TASK_STATUS_DONE
    #   改成 tasks.remove(task)  # 🐛 错误：变成删除了！
    #
    # 然后运行本测试，观察测试失败，再修复回正确实现。
    # =====================================================================

    def test_complete_task_preserves_record_not_deletes_it(self, temp_tasks_file):
        """【Bug 防护】完成任务应保留记录，而非删除。

        如果你把 complete_task 误写成删除任务，
        本测试会失败并告诉你具体哪里不对。
        """
        add_task("不应被删除的任务")
        complete_task(1)

        # 完成后任务应该仍在列表中
        task = get_task_by_id(1)
        assert task is not None, "BUG: 任务被删除了！完成任务不应删除记录"
        assert task["status"] == "done"

        # 总数应该仍然为 1
        all_tasks = get_all_tasks()
        assert len(all_tasks) == 1, "BUG: 完成任务后任务数量变少了！"
