"""临时脚本：解决合并冲突，生成包含 deadline + priority 双功能的文件。"""
import pathlib

BASE = pathlib.Path(__file__).parent

# ── conftest.py ──
(BASE / "tests" / "conftest.py").write_text(r"""
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
    {"id": 1, "title": "完成实验报告", "status": "pending", "created_at": "2026-06-14 10:00:00", "deadline": "2026-06-20", "priority": "high"},
    {"id": 2, "title": "复习高等数学", "status": "done",    "created_at": "2026-06-14 10:01:00", "deadline": None,           "priority": "medium"},
    {"id": 3, "title": "去图书馆学习", "status": "pending", "created_at": "2026-06-14 10:02:00", "deadline": "2026-01-01", "priority": "low"},
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
""".lstrip(), encoding="utf-8")

# ── test_task_model.py ──
(BASE / "tests" / "test_task_model.py").write_text(r'''
"""
test_task_model.py —— 测试 task_model 模块

测试范围：
  - create_task() 工厂函数（含 deadline + priority）
  - validate_title() 校验规则
  - validate_deadline() 截止日期校验
  - validate_priority() 优先级校验
  - is_valid_task() 结构校验
  - 状态常量定义
"""

import re
from task_model import (
    create_task,
    validate_title,
    validate_deadline,
    validate_priority,
    is_valid_task,
    TASK_STATUS_PENDING,
    TASK_STATUS_DONE,
    TASK_REQUIRED_FIELDS,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    PRIORITY_HIGH,
)


# ============================================================================
# 测试 create_task()
# ============================================================================

class TestCreateTask:
    """测试任务创建工厂函数。"""

    def test_create_task_returns_dict_with_required_fields(self):
        """【正常】create_task 返回包含必需字段的字典。"""
        task = create_task(1, "测试任务")

        assert isinstance(task, dict)
        assert "id" in task
        assert "title" in task
        assert "status" in task
        assert "created_at" in task
        assert "deadline" in task
        assert "priority" in task

    def test_create_task_sets_correct_id_and_title(self):
        """【正常】create_task 正确设置编号和标题。"""
        task = create_task(42, "完成作业")

        assert task["id"] == 42
        assert task["title"] == "完成作业"

    def test_create_task_defaults_to_pending(self):
        """【正常】新创建的任务状态默认为 pending。"""
        task = create_task(1, "某项任务")

        assert task["status"] == TASK_STATUS_PENDING
        assert task["status"] == "pending"

    def test_create_task_timestamp_format(self):
        """【正常】created_at 字段格式为 YYYY-MM-DD HH:MM:SS。"""
        task = create_task(1, "检查时间格式")

        pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"
        assert re.match(pattern, task["created_at"]), f"时间格式不正确: {task['created_at']}"

    def test_create_task_with_deadline(self):
        """【正常】create_task 支持可选 deadline 参数。"""
        task = create_task(1, "交报告", deadline="2026-06-20")
        assert task["deadline"] == "2026-06-20"

    def test_create_task_without_deadline(self):
        """【正常】创建任务不提供 deadline 时默认为 None。"""
        task = create_task(1, "无截止日期")
        assert task["deadline"] is None

    def test_create_task_with_high_priority(self):
        """【正常】create_task 支持创建高优先级任务。"""
        task = create_task(1, "紧急任务", priority="high")
        assert task["priority"] == "high"

    def test_create_task_default_priority_is_medium(self):
        """【正常】不指定优先级时默认为 medium。"""
        task = create_task(1, "普通任务")
        assert task["priority"] == "medium"

    def test_create_task_with_both_deadline_and_priority(self):
        """【正常】同时指定截止日期和优先级。"""
        task = create_task(1, "完整任务", deadline="2026-12-31", priority="high")
        assert task["deadline"] == "2026-12-31"
        assert task["priority"] == "high"


# ============================================================================
# 测试 validate_title()
# ============================================================================

class TestValidateTitle:
    """测试标题校验函数。"""

    def test_valid_title_returns_none(self):
        """【正常】合法标题返回 None。"""
        assert validate_title("完成实验报告") is None

    def test_empty_title_returns_error(self):
        """【边界】空字符串返回错误信息。"""
        error = validate_title("")
        assert error is not None
        assert "不能为空" in error

    def test_title_too_long_returns_error(self):
        """【边界】超过 200 字符的标题返回错误信息。"""
        long_title = "很" * 201
        error = validate_title(long_title)
        assert error is not None
        assert "200" in error

    def test_title_exactly_200_chars_ok(self):
        """【边界】恰好 200 字符的标题合法。"""
        title_200 = "很" * 200
        assert validate_title(title_200) is None


# ============================================================================
# 测试 validate_deadline()
# ============================================================================

class TestValidateDeadline:
    """测试截止日期校验函数（实验4 新增）。"""

    def test_valid_deadline_returns_none(self):
        assert validate_deadline("2026-12-31") is None

    def test_none_deadline_returns_none(self):
        assert validate_deadline(None) is None

    def test_bad_format_returns_error(self):
        error = validate_deadline("2026/12/31")
        assert error is not None
        assert "YYYY-MM-DD" in error

    def test_invalid_date_returns_error(self):
        error = validate_deadline("2026-02-30")
        assert error is not None
        assert "不是合法的日期" in error

    def test_short_string_returns_error(self):
        error = validate_deadline("abc")
        assert error is not None
        assert "YYYY-MM-DD" in error


# ============================================================================
# 测试 validate_priority()
# ============================================================================

class TestValidatePriority:
    """测试优先级校验函数（实验4 新增）。"""

    def test_valid_high(self):
        assert validate_priority("high") is None

    def test_valid_medium(self):
        assert validate_priority("medium") is None

    def test_valid_low(self):
        assert validate_priority("low") is None

    def test_invalid_priority_returns_error(self):
        error = validate_priority("urgent")
        assert error is not None

    def test_empty_priority_returns_error(self):
        error = validate_priority("")
        assert error is not None


# ============================================================================
# 测试 is_valid_task()
# ============================================================================

class TestIsValidTask:
    """测试任务字典结构校验。"""

    def test_valid_task_returns_true(self):
        task = {"id": 1, "title": "测试", "status": "pending", "created_at": "2026-06-14 10:00:00", "deadline": None, "priority": "medium"}
        assert is_valid_task(task) is True

    def test_missing_field_returns_false(self):
        task = {"id": 1, "title": "测试"}
        assert is_valid_task(task) is False

    def test_wrong_type_returns_false(self):
        task = {"id": "不是数字", "title": "测试", "status": "pending", "created_at": "2026-06-14 10:00:00", "deadline": None, "priority": "medium"}
        assert is_valid_task(task) is False


# ============================================================================
# 测试状态常量
# ============================================================================

class TestStatusConstants:
    """验证状态常量定义正确。"""

    def test_pending_constant(self):
        assert TASK_STATUS_PENDING == "pending"

    def test_done_constant(self):
        assert TASK_STATUS_DONE == "done"

    def test_required_fields_structure(self):
        """验证 TASK_REQUIRED_FIELDS 包含六个字段（含 deadline + priority）。"""
        assert "id" in TASK_REQUIRED_FIELDS
        assert "title" in TASK_REQUIRED_FIELDS
        assert "status" in TASK_REQUIRED_FIELDS
        assert "created_at" in TASK_REQUIRED_FIELDS
        assert "deadline" in TASK_REQUIRED_FIELDS
        assert "priority" in TASK_REQUIRED_FIELDS
        assert TASK_REQUIRED_FIELDS["id"] == int
        assert TASK_REQUIRED_FIELDS["title"] == str
        assert TASK_REQUIRED_FIELDS["priority"] == str

    def test_priority_constants(self):
        assert PRIORITY_LOW == "low"
        assert PRIORITY_MEDIUM == "medium"
        assert PRIORITY_HIGH == "high"
'''.lstrip(), encoding="utf-8")

print("All conflict files resolved!")
