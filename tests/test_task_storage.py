import json
import os
from task_storage import load_tasks, save_tasks


class TestLoadTasks:

    def test_empty_dir_returns_empty_list(self, temp_tasks_file):
        assert not os.path.exists(str(temp_tasks_file))
        tasks = load_tasks()
        assert tasks == []
        assert isinstance(tasks, list)

    def test_existing_file_returns_data(self, temp_tasks_file_with_data):
        tasks = load_tasks()
        assert len(tasks) == 3
        assert tasks[0]["id"] == 1
        assert tasks[0]["title"] == "完成实验报告"

    def test_corrupted_json_returns_empty_list(self, temp_tasks_file_corrupted):
        tasks = load_tasks()
        assert tasks == []
        assert isinstance(tasks, list)

    def test_empty_file_returns_empty_list(self, temp_tasks_file):
        """BUG-001: 空 tasks.json 不应导致程序崩溃"""
        temp_tasks_file.write_text('', encoding='utf-8')
        tasks = load_tasks()
        assert tasks == []
        assert isinstance(tasks, list)

    def test_non_list_json_returns_empty_list(self, temp_tasks_file, monkeypatch):
        temp_tasks_file.write_text('{"key": "value"}', encoding="utf-8")
        monkeypatch.setattr("task_storage.TASKS_FILE", str(temp_tasks_file))
        tasks = load_tasks()
        assert tasks == []


class TestSaveTasks:

    def test_creates_file(self, temp_tasks_file):
        save_tasks([{"id": 1, "title": "测试", "status": "pending", "created_at": "2026-06-14 10:00:00", "deadline": None, "priority": "medium"}])
        assert os.path.exists(str(temp_tasks_file))

    def test_writes_valid_json(self, temp_tasks_file):
        tasks = [
            {"id": 1, "title": "任务A", "status": "pending", "created_at": "2026-06-14 10:00:00", "deadline": None, "priority": "high"},
            {"id": 2, "title": "任务B", "status": "done", "created_at": "2026-06-14 10:01:00", "deadline": None, "priority": "medium"},
        ]
        save_tasks(tasks)
        with open(str(temp_tasks_file), "r", encoding="utf-8") as f:
            loaded = json.load(f)
        assert isinstance(loaded, list)
        assert len(loaded) == 2
        assert loaded[0]["title"] == "任务A"
        assert loaded[1]["status"] == "done"

    def test_preserves_unicode(self, temp_tasks_file):
        save_tasks([{"id": 1, "title": "完成实验报告", "status": "pending", "created_at": "2026-06-14 10:00:00", "deadline": None, "priority": "medium"}])
        content = open(str(temp_tasks_file), "r", encoding="utf-8").read()
        assert "完成实验报告" in content

    def test_overwrites_previous_data(self, temp_tasks_file):
        save_tasks([{"id": 1, "title": "旧数据", "status": "pending", "created_at": "2026-06-14 10:00:00", "deadline": None, "priority": "medium"}])
        save_tasks([{"id": 2, "title": "新数据", "status": "done", "created_at": "2026-06-14 10:01:00", "deadline": None, "priority": "medium"}])
        loaded = load_tasks()
        assert len(loaded) == 1
        assert loaded[0]["title"] == "新数据"


class TestRoundtrip:

    def test_preserves_all_fields(self, temp_tasks_file):
        original = [
            {"id": 1, "title": "任务1", "status": "pending", "created_at": "2026-06-14 10:00:00", "deadline": "2026-06-20", "priority": "high"},
            {"id": 2, "title": "任务2", "status": "done", "created_at": "2026-06-14 10:01:00", "deadline": None, "priority": "medium"},
        ]
        save_tasks(original)
        loaded = load_tasks()
        assert loaded == original
        for orig, reloaded in zip(original, loaded):
            for key in ("id", "title", "status", "created_at", "deadline", "priority"):
                assert orig[key] == reloaded[key]

    def test_preserves_deadline(self, temp_tasks_file):
        original = [
            {"id": 1, "title": "有截止日期", "status": "pending", "created_at": "2026-06-14 10:00:00", "deadline": "2026-12-31", "priority": "medium"},
            {"id": 2, "title": "无截止日期", "status": "pending", "created_at": "2026-06-14 10:01:00", "deadline": None, "priority": "medium"},
        ]
        save_tasks(original)
        loaded = load_tasks()
        assert loaded[0]["deadline"] == "2026-12-31"
        assert loaded[1]["deadline"] is None

    def test_preserves_priority(self, temp_tasks_file):
        original = [
            {"id": 1, "title": "高", "status": "pending", "created_at": "2026-06-14 10:00:00", "deadline": None, "priority": "high"},
            {"id": 2, "title": "中", "status": "pending", "created_at": "2026-06-14 10:01:00", "deadline": None, "priority": "medium"},
            {"id": 3, "title": "低", "status": "pending", "created_at": "2026-06-14 10:02:00", "deadline": None, "priority": "low"},
        ]
        save_tasks(original)
        loaded = load_tasks()
        assert loaded[0]["priority"] == "high"
        assert loaded[1]["priority"] == "medium"
        assert loaded[2]["priority"] == "low"
