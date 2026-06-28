import json
import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

SAMPLE_TASKS = [
    {"id": 1, "title": "完成实验报告", "status": "pending", "created_at": "2026-06-14 10:00:00", "deadline": "2026-06-20", "priority": "high"},
    {"id": 2, "title": "复习高等数学", "status": "done",    "created_at": "2026-06-14 10:01:00", "deadline": None,           "priority": "medium"},
    {"id": 3, "title": "去图书馆学习", "status": "pending", "created_at": "2026-06-14 10:02:00", "deadline": "2026-01-01", "priority": "low"},
]


@pytest.fixture
def temp_tasks_file(tmp_path, monkeypatch):
    temp_file = tmp_path / "tasks.json"
    monkeypatch.setattr("task_storage.TASKS_FILE", str(temp_file))
    yield temp_file


@pytest.fixture
def temp_tasks_file_with_data(tmp_path, monkeypatch):
    temp_file = tmp_path / "tasks.json"
    temp_file.write_text(json.dumps(SAMPLE_TASKS, ensure_ascii=False, indent=2), encoding="utf-8")
    monkeypatch.setattr("task_storage.TASKS_FILE", str(temp_file))
    yield temp_file


@pytest.fixture
def temp_tasks_file_corrupted(tmp_path, monkeypatch):
    temp_file = tmp_path / "tasks.json"
    temp_file.write_text("这不是合法的 JSON {{{[[[", encoding="utf-8")
    monkeypatch.setattr("task_storage.TASKS_FILE", str(temp_file))
    yield temp_file
