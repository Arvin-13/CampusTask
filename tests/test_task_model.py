"""
test_task_model.py —— 测试 task_model 模块

测试范围：
  - create_task() 工厂函数
  - validate_title() 校验规则
  - is_valid_task() 结构校验
  - 状态常量定义
"""

import re
from task_model import (
    create_task,
    validate_title,
    is_valid_task,
    TASK_STATUS_PENDING,
    TASK_STATUS_DONE,
    TASK_REQUIRED_FIELDS,
)


# ============================================================================
# 测试 create_task()
# ============================================================================

class TestCreateTask:
    """测试任务创建工厂函数。"""

    def test_create_task_returns_dict_with_required_fields(self):
        """【正常】create_task 返回包含 id/title/status/created_at 的字典。"""
        task = create_task(1, "测试任务")

        assert isinstance(task, dict)
        assert "id" in task
        assert "title" in task
        assert "status" in task
        assert "created_at" in task

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

        # 验证时间格式: 2026-06-14 10:30:45
        pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"
        assert re.match(pattern, task["created_at"]), f"时间格式不正确: {task['created_at']}"


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
# 测试 is_valid_task()
# ============================================================================

class TestIsValidTask:
    """测试任务字典结构校验。"""

    def test_valid_task_returns_true(self):
        """【正常】包含所有必需字段且类型正确的任务返回 True。"""
        task = {"id": 1, "title": "测试", "status": "pending", "created_at": "2026-06-14 10:00:00"}
        assert is_valid_task(task) is True

    def test_missing_field_returns_false(self):
        """【边界】缺少字段的任务返回 False。"""
        task = {"id": 1, "title": "测试"}  # 缺少 status 和 created_at
        assert is_valid_task(task) is False

    def test_wrong_type_returns_false(self):
        """【边界】字段类型错误返回 False。"""
        task = {"id": "不是数字", "title": "测试", "status": "pending", "created_at": "2026-06-14 10:00:00"}
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
        """验证 TASK_REQUIRED_FIELDS 包含四个字段。"""
        assert "id" in TASK_REQUIRED_FIELDS
        assert "title" in TASK_REQUIRED_FIELDS
        assert "status" in TASK_REQUIRED_FIELDS
        assert "created_at" in TASK_REQUIRED_FIELDS
        assert TASK_REQUIRED_FIELDS["id"] == int
        assert TASK_REQUIRED_FIELDS["title"] == str
