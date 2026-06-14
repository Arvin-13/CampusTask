"""
test_task_storage.py —— 测试 task_storage 模块

测试范围：
  - load_tasks() 在文件不存在/存在/损坏时的行为
  - save_tasks() 正常保存
  - 数据持久化往返验证
"""

import json
import os
from task_storage import load_tasks, save_tasks, TASKS_FILE


# ============================================================================
# 测试 load_tasks()
# ============================================================================

class TestLoadTasks:
    """测试从 JSON 文件加载任务。"""

    def test_load_from_empty_dir_returns_empty_list(self, temp_tasks_file):
        """【测试用例7/12】文件不存在时返回空列表，不报错。"""
        # temp_tasks_file 在临时目录，此时 tasks.json 尚不存在
        assert not os.path.exists(str(temp_tasks_file))
        tasks = load_tasks()
        assert tasks == []
        assert isinstance(tasks, list)

    def test_load_from_existing_file_returns_data(self, temp_tasks_file_with_data):
        """【正常】从已有 JSON 文件加载任务列表。"""
        tasks = load_tasks()
        assert len(tasks) == 3
        assert tasks[0]["id"] == 1
        assert tasks[0]["title"] == "完成实验报告"

    def test_load_corrupted_json_returns_empty_list(self, temp_tasks_file_corrupted):
        """【测试用例8/12】JSON 文件损坏时返回空列表，不崩溃。"""
        tasks = load_tasks()
        assert tasks == []
        assert isinstance(tasks, list)

    def test_load_non_list_json_returns_empty_list(self, temp_tasks_file, monkeypatch):
        """【边界】JSON 内容不是数组时返回空列表。"""
        temp_tasks_file.write_text('{"key": "value"}', encoding="utf-8")
        monkeypatch.setattr("task_storage.TASKS_FILE", str(temp_tasks_file))
        tasks = load_tasks()
        assert tasks == []


# ============================================================================
# 测试 save_tasks()
# ============================================================================

class TestSaveTasks:
    """测试将任务列表保存到 JSON 文件。"""

    def test_save_creates_file(self, temp_tasks_file):
        """【正常】save_tasks 能创建 JSON 文件。"""
        tasks = [{"id": 1, "title": "测试", "status": "pending", "created_at": "2026-06-14 10:00:00"}]
        save_tasks(tasks)

        assert os.path.exists(str(temp_tasks_file))

    def test_save_writes_valid_json(self, temp_tasks_file):
        """【正常】保存的文件内容是合法 JSON 数组。"""
        tasks = [
            {"id": 1, "title": "任务A", "status": "pending", "created_at": "2026-06-14 10:00:00"},
            {"id": 2, "title": "任务B", "status": "done", "created_at": "2026-06-14 10:01:00"},
        ]
        save_tasks(tasks)

        with open(str(temp_tasks_file), "r", encoding="utf-8") as f:
            loaded = json.load(f)
        assert isinstance(loaded, list)
        assert len(loaded) == 2
        assert loaded[0]["title"] == "任务A"
        assert loaded[1]["status"] == "done"

    def test_save_preserves_unicode(self, temp_tasks_file):
        """【正常】保存时正确保留中文字符。"""
        tasks = [{"id": 1, "title": "完成实验报告📝", "status": "pending", "created_at": "2026-06-14 10:00:00"}]
        save_tasks(tasks)

        with open(str(temp_tasks_file), "r", encoding="utf-8") as f:
            content = f.read()
        assert "完成实验报告📝" in content

    def test_save_overwrites_previous_data(self, temp_tasks_file):
        """【正常】保存会覆盖旧数据，不会追加。"""
        # 第一次保存
        save_tasks([{"id": 1, "title": "旧数据", "status": "pending", "created_at": "2026-06-14 10:00:00"}])
        # 第二次保存
        save_tasks([{"id": 2, "title": "新数据", "status": "done", "created_at": "2026-06-14 10:01:00"}])

        loaded = load_tasks()
        assert len(loaded) == 1
        assert loaded[0]["title"] == "新数据"


# ============================================================================
# 测试数据持久化往返
# ============================================================================

class TestPersistenceRoundtrip:
    """测试保存→加载的完整往返流程。"""

    def test_roundtrip_preserves_all_fields(self, temp_tasks_file):
        """【测试用例10/12】保存后再加载，所有字段保持一致。"""
        original = [
            {"id": 1, "title": "任务1", "status": "pending", "created_at": "2026-06-14 10:00:00"},
            {"id": 2, "title": "任务2", "status": "done", "created_at": "2026-06-14 10:01:00"},
        ]
        save_tasks(original)
        loaded = load_tasks()

        assert loaded == original
        assert len(loaded) == 2
        for orig, reloaded in zip(original, loaded):
            assert orig["id"] == reloaded["id"]
            assert orig["title"] == reloaded["title"]
            assert orig["status"] == reloaded["status"]
            assert orig["created_at"] == reloaded["created_at"]
