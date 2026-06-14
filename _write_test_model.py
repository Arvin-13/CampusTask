"""Write the resolved test_task_model.py"""
import pathlib

content = '''"""
test_task_model.py -- test task_model module

Tests:
  - create_task() factory (with deadline + priority)
  - validate_title()
  - validate_deadline()
  - validate_priority()
  - is_valid_task()
  - status/priority constants
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


class TestCreateTask:

    def test_create_task_returns_dict_with_required_fields(self):
        task = create_task(1, "test")
        assert isinstance(task, dict)
        assert "id" in task
        assert "title" in task
        assert "status" in task
        assert "created_at" in task
        assert "deadline" in task
        assert "priority" in task

    def test_create_task_sets_correct_id_and_title(self):
        task = create_task(42, "homework")
        assert task["id"] == 42
        assert task["title"] == "homework"

    def test_create_task_defaults_to_pending(self):
        task = create_task(1, "a task")
        assert task["status"] == TASK_STATUS_PENDING

    def test_create_task_timestamp_format(self):
        task = create_task(1, "time check")
        pattern = r"^\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}$"
        assert re.match(pattern, task["created_at"]), f"Bad format: {task['created_at']}"

    def test_create_task_with_deadline(self):
        task = create_task(1, "report", deadline="2026-06-20")
        assert task["deadline"] == "2026-06-20"

    def test_create_task_without_deadline(self):
        task = create_task(1, "no deadline")
        assert task["deadline"] is None

    def test_create_task_with_high_priority(self):
        task = create_task(1, "urgent", priority="high")
        assert task["priority"] == "high"

    def test_create_task_default_priority_is_medium(self):
        task = create_task(1, "normal")
        assert task["priority"] == "medium"

    def test_create_task_with_both_deadline_and_priority(self):
        task = create_task(1, "full", deadline="2026-12-31", priority="high")
        assert task["deadline"] == "2026-12-31"
        assert task["priority"] == "high"


class TestValidateTitle:

    def test_valid_title_returns_none(self):
        assert validate_title("finish report") is None

    def test_empty_title_returns_error(self):
        error = validate_title("")
        assert error is not None
        assert "not empty" in error.lower() or "不能为空" in error

    def test_title_too_long_returns_error(self):
        error = validate_title("a" * 201)
        assert error is not None
        assert "200" in error

    def test_title_exactly_200_chars_ok(self):
        assert validate_title("a" * 200) is None


class TestValidateDeadline:

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

    def test_short_string_returns_error(self):
        error = validate_deadline("abc")
        assert error is not None
        assert "YYYY-MM-DD" in error


class TestValidatePriority:

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


class TestIsValidTask:

    def test_valid_task_returns_true(self):
        task = {"id": 1, "title": "test", "status": "pending", "created_at": "2026-06-14 10:00:00", "deadline": None, "priority": "medium"}
        assert is_valid_task(task) is True

    def test_missing_field_returns_false(self):
        task = {"id": 1, "title": "test"}
        assert is_valid_task(task) is False

    def test_wrong_type_returns_false(self):
        task = {"id": "not-int", "title": "test", "status": "pending", "created_at": "2026-06-14 10:00:00", "deadline": None, "priority": "medium"}
        assert is_valid_task(task) is False


class TestStatusConstants:

    def test_pending_constant(self):
        assert TASK_STATUS_PENDING == "pending"

    def test_done_constant(self):
        assert TASK_STATUS_DONE == "done"

    def test_required_fields_structure(self):
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
'''

pathlib.Path('tests/test_task_model.py').write_text(content, encoding='utf-8')
print('test_task_model.py written')
