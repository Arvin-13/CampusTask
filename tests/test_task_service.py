import pytest
from task_service import (
    add_task, get_all_tasks, get_pending_tasks, get_done_tasks,
    get_overdue_tasks, get_tasks_by_priority, get_tasks_sorted_by_deadline,
    search_tasks, get_task_by_id, complete_task, get_statistics,
)


class TestAddTask:

    def test_success(self, temp_tasks_file):
        task = add_task("完成软件工程实验3")
        assert task["id"] == 1
        assert task["title"] == "完成软件工程实验3"
        assert task["status"] == "pending"
        assert "created_at" in task
        assert "deadline" in task
        assert "priority" in task

    def test_trims_whitespace(self, temp_tasks_file):
        assert add_task("  去图书馆  ")["title"] == "去图书馆"

    def test_empty_title_raises_error(self, temp_tasks_file):
        with pytest.raises(ValueError, match="不能为空"):
            add_task("")

    def test_whitespace_only_raises_error(self, temp_tasks_file):
        with pytest.raises(ValueError):
            add_task("   ")

    def test_title_exceeding_200_chars_raises_error(self, temp_tasks_file):
        with pytest.raises(ValueError, match="200"):
            add_task("长" * 201)

    def test_id_increments(self, temp_tasks_file):
        t1 = add_task("任务A")
        t2 = add_task("任务B")
        t3 = add_task("任务C")
        assert t1["id"] == 1
        assert t2["id"] == 2
        assert t3["id"] == 3

    def test_persists_to_file(self, temp_tasks_file):
        add_task("持久化测试")
        tasks = get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "持久化测试"

    def test_with_deadline(self, temp_tasks_file):
        assert add_task("交报告", deadline="2026-12-31")["deadline"] == "2026-12-31"

    def test_without_deadline(self, temp_tasks_file):
        assert add_task("无截止日期")["deadline"] is None

    def test_invalid_deadline_raises_error(self, temp_tasks_file):
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            add_task("格式错误", deadline="2026/12/31")

    def test_nonexistent_date_raises_error(self, temp_tasks_file):
        with pytest.raises(ValueError, match="不是合法的日期"):
            add_task("日期不存在", deadline="2026-02-30")

    def test_high_priority(self, temp_tasks_file):
        assert add_task("紧急任务", priority="high")["priority"] == "high"

    def test_default_priority_is_medium(self, temp_tasks_file):
        assert add_task("普通任务")["priority"] == "medium"

    def test_invalid_priority_raises_error(self, temp_tasks_file):
        with pytest.raises(ValueError):
            add_task("测试", priority="urgent")

    def test_both_deadline_and_priority(self, temp_tasks_file):
        task = add_task("完整任务", deadline="2026-12-31", priority="high")
        assert task["deadline"] == "2026-12-31"
        assert task["priority"] == "high"


class TestQueryTasks:

    def test_all_empty(self, temp_tasks_file):
        assert get_all_tasks() == []

    def test_sorted_by_priority(self, temp_tasks_file):
        add_task("低优先", priority="low")
        add_task("高优先", priority="high")
        add_task("中优先", priority="medium")
        priorities = [t.get("priority") for t in get_all_tasks()]
        assert priorities[0] == "high"
        assert len(priorities) == 3

    def test_pending_only(self, temp_tasks_file_with_data):
        pending = get_pending_tasks()
        assert all(t["status"] == "pending" for t in pending)
        assert len(pending) == 2

    def test_done_only(self, temp_tasks_file_with_data):
        done = get_done_tasks()
        assert all(t["status"] == "done" for t in done)
        assert len(done) == 1

    def test_by_id_exists(self, temp_tasks_file_with_data):
        task = get_task_by_id(2)
        assert task and task["title"] == "复习高等数学"

    def test_by_id_not_exists(self, temp_tasks_file_with_data):
        assert get_task_by_id(999) is None


class TestOverdueTasks:

    def test_detected(self, temp_tasks_file):
        add_task("昨天截止", deadline="2020-01-01")
        add_task("未来截止", deadline="2099-12-31")
        overdue = get_overdue_tasks()
        assert len(overdue) == 1
        assert overdue[0]["title"] == "昨天截止"

    def test_none_when_all_future(self, temp_tasks_file):
        add_task("未来任务", deadline="2099-12-31")
        assert get_overdue_tasks() == []

    def test_excludes_done(self, temp_tasks_file):
        add_task("过期但已完成", deadline="2020-01-01")
        complete_task(1)
        assert len(get_overdue_tasks()) == 0

    def test_from_sample_data(self, temp_tasks_file_with_data):
        overdue = get_overdue_tasks()
        assert any(t["id"] == 3 for t in overdue)


class TestPriorityFiltering:

    def test_filter_high(self, temp_tasks_file_with_data):
        tasks = get_tasks_by_priority("high")
        assert len(tasks) >= 1
        assert all(t["priority"] == "high" for t in tasks)


class TestCompleteTask:

    def test_existing(self, temp_tasks_file_with_data):
        task = complete_task(1)
        assert task["id"] == 1 and task["status"] == "done"

    def test_nonexistent_raises_error(self, temp_tasks_file_with_data):
        with pytest.raises(LookupError, match="未找到"):
            complete_task(999)

    def test_already_done_raises_error(self, temp_tasks_file_with_data):
        with pytest.raises(ValueError, match="已经完成"):
            complete_task(2)

    def test_second_time_fails(self, temp_tasks_file):
        add_task("测试重复完成")
        complete_task(1)
        with pytest.raises(ValueError, match="已经完成"):
            complete_task(1)

    def test_changes_status_in_storage(self, temp_tasks_file):
        add_task("临时任务")
        complete_task(1)
        assert get_task_by_id(1)["status"] == "done"


class TestStatistics:

    def test_empty(self, temp_tasks_file):
        stats = get_statistics()
        assert stats == {"total": 0, "pending": 0, "done": 0, "overdue": 0}

    def test_with_data(self, temp_tasks_file_with_data):
        stats = get_statistics()
        assert stats["total"] == 3
        assert stats["pending"] == 2
        assert stats["done"] == 1

    def test_after_completing_all(self, temp_tasks_file):
        add_task("任务1")
        add_task("任务2")
        complete_task(1)
        complete_task(2)
        stats = get_statistics()
        assert stats["total"] == 2
        assert stats["pending"] == 0
        assert stats["done"] == 2


class TestDataConsistency:

    def test_persists_after_multiple_operations(self, temp_tasks_file):
        add_task("任务A")
        add_task("任务B")
        complete_task(1)
        assert len(get_all_tasks()) == 2

    def test_id_continues_after_load(self, temp_tasks_file_with_data):
        assert add_task("新任务")["id"] == 4

    def test_complete_preserves_not_deletes(self, temp_tasks_file):
        add_task("不应被删除的任务")
        complete_task(1)
        task = get_task_by_id(1)
        assert task is not None, "BUG: 任务被删除了！"
        assert task["status"] == "done"
        assert len(get_all_tasks()) == 1


class TestDeadlineSorting:

    def test_sorted_by_deadline_ascending(self, temp_tasks_file):
        add_task("任务A", deadline="2026-12-31")
        add_task("任务B", deadline="2026-06-15")
        add_task("任务C", deadline="2026-06-01")
        deadlines = [t.get("deadline") for t in get_tasks_sorted_by_deadline()]
        assert deadlines == ["2026-06-01", "2026-06-15", "2026-12-31"]

    def test_no_deadline_go_last(self, temp_tasks_file):
        add_task("无截止日期")
        add_task("有截止日期", deadline="2026-06-15")
        tasks = get_tasks_sorted_by_deadline()
        assert tasks[0]["deadline"] == "2026-06-15"
        assert tasks[1]["deadline"] is None

    def test_mixed_priorities(self, temp_tasks_file):
        add_task("高优先", priority="high", deadline="2026-12-31")
        add_task("低优先", priority="low", deadline="2026-06-15")
        tasks = get_tasks_sorted_by_deadline()
        assert tasks[0]["title"] == "低优先"
        assert tasks[1]["title"] == "高优先"


class TestTaskSearch:

    def test_exact_match(self, temp_tasks_file):
        add_task("完成软件工程实验")
        add_task("复习高等数学")
        add_task("提交物理实验报告")
        results = search_tasks("实验")
        assert len(results) == 2
        assert any(t["title"] == "完成软件工程实验" for t in results)
        assert any(t["title"] == "提交物理实验报告" for t in results)

    def test_case_insensitive(self, temp_tasks_file):
        add_task("Submit Software Engineering Report")
        assert len(search_tasks("software")) == 1
        assert len(search_tasks("SOFTWARE")) == 1

    def test_partial_match(self, temp_tasks_file):
        add_task("提交物理实验报告")
        assert len(search_tasks("物理")) == 1

    def test_empty_keyword(self, temp_tasks_file):
        add_task("测试任务")
        assert search_tasks("") == []
        assert search_tasks("   ") == []

    def test_no_results(self, temp_tasks_file):
        add_task("完成实验报告")
        assert search_tasks("不存在的关键词") == []

    def test_across_statuses(self, temp_tasks_file):
        add_task("待完成任务")
        add_task("已完成任务")
        complete_task(2)
        assert len(search_tasks("任务")) == 2
