"""
conftest.py —— pytest 共享 fixture

提供测试中复用的数据构造和临时文件管理。
"""

import json
import os
import sys
import pytest

# 确保项目根目录在 sys.path 中，方便测试文件 import 项目模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ---------------------------------------------------------------------------
# 测试数据
# ---------------------------------------------------------------------------

SAMPLE_TASKS = [
    {"id": 1, "title": "完成实验报告", "status": "pending", "created_at": "2026-06-14 10:00:00", "priority": "high"},
    {"id": 2, "title": "复习高等数学", "status": "done",    "created_at": "2026-06-14 10:01:00", "priority": "medium"},
    {"id": 3, "title": "去图书馆学习", "status": "pending", "created_at": "2026-06-14 10:02:00", "priority": "low"},
]


# ---------------------------------------------------------------------------
# 临时 tasks.json 路径管理
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_tasks_file(tmp_path, monkeypatch):
    """在临时目录中使用独立的 tasks.json，避免污染真实数据。

    monkeypatch 会把 task_storage.TASKS_FILE 改指向临时文件，
    测试结束后自动还原。
    """
    temp_file = tmp_path / "tasks.json"
    monkeypatch.setattr("task_storage.TASKS_FILE", str(temp_file))
    yield temp_file


@pytest.fixture
def temp_tasks_file_with_data(tmp_path, monkeypatch):
    """创建一个已有示例数据的临时 tasks.json。"""
    temp_file = tmp_path / "tasks.json"
    temp_file.write_text(json.dumps(SAMPLE_TASKS, ensure_ascii=False, indent=2), encoding="utf-8")
    monkeypatch.setattr("task_storage.TASKS_FILE", str(temp_file))
    yield temp_file


@pytest.fixture
def temp_tasks_file_corrupted(tmp_path, monkeypatch):
    """创建一个内容损坏的临时 tasks.json。"""
    temp_file = tmp_path / "tasks.json"
    temp_file.write_text("这不是合法的 JSON {{{[[[", encoding="utf-8")
    monkeypatch.setattr("task_storage.TASKS_FILE", str(temp_file))
    yield temp_file
