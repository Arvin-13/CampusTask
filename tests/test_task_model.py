import re
from task_model import (
    create_task, validate_title, validate_deadline, validate_priority,
    is_valid_task, TASK_STATUS_PENDING, TASK_STATUS_DONE,
    TASK_REQUIRED_FIELDS, PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH,
)


class TestCreateTask:

    def test_returns_dict_with_required_fields(self):
        task = create_task(1, "test")
        assert isinstance(task, dict)
        for key in ("id", "title", "status", "created_at", "deadline", "priority"):
            assert key in task

    def test_sets_correct_id_and_title(self):
        task = create_task(42, "homework")
        assert task["id"] == 42
        assert task["title"] == "homework"

    def test_defaults_to_pending(self):
        assert create_task(1, "a task")["status"] == TASK_STATUS_PENDING

    def test_timestamp_format(self):
        task = create_task(1, "time check")
        assert re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", task["created_at"])

    def test_with_deadline(self):
        assert create_task(1, "report", deadline="2026-06-20")["deadline"] == "2026-06-20"

    def test_without_deadline(self):
        assert create_task(1, "no deadline")["deadline"] is None

    def test_with_high_priority(self):
        assert create_task(1, "urgent", priority="high")["priority"] == "high"

    def test_default_priority_is_medium(self):
        assert create_task(1, "normal")["priority"] == "medium"

    def test_with_both_deadline_and_priority(self):
        task = create_task(1, "full", deadline="2026-12-31", priority="high")
        assert task["deadline"] == "2026-12-31"
        assert task["priority"] == "high"


class TestValidateTitle:

    def test_valid_returns_none(self):
        assert validate_title("finish report") is None

    def test_empty_returns_error(self):
        err = validate_title("")
        assert err and ("not empty" in err.lower() or "不能为空" in err)

    def test_too_long_returns_error(self):
        err = validate_title("a" * 201)
        assert err and "200" in err

    def test_exactly_200_chars_ok(self):
        assert validate_title("a" * 200) is None


class TestValidateDeadline:

    def test_valid_returns_none(self):
        assert validate_deadline("2026-12-31") is None

    def test_none_returns_none(self):
        assert validate_deadline(None) is None

    def test_bad_format_returns_error(self):
        err = validate_deadline("2026/12/31")
        assert err and "YYYY-MM-DD" in err

    def test_invalid_date_returns_error(self):
        assert validate_deadline("2026-02-30") is not None

    def test_short_string_returns_error(self):
        err = validate_deadline("abc")
        assert err and "YYYY-MM-DD" in err


class TestValidatePriority:

    def test_valid_high(self):
        assert validate_priority("high") is None

    def test_valid_medium(self):
        assert validate_priority("medium") is None

    def test_valid_low(self):
        assert validate_priority("low") is None

    def test_invalid_returns_error(self):
        assert validate_priority("urgent") is not None

    def test_empty_returns_error(self):
        assert validate_priority("") is not None


class TestIsValidTask:

    def test_valid_task_returns_true(self):
        task = {"id": 1, "title": "t", "status": "pending", "created_at": "2026-06-14 10:00:00", "deadline": None, "priority": "medium"}
        assert is_valid_task(task) is True

    def test_missing_field_returns_false(self):
        assert is_valid_task({"id": 1, "title": "t"}) is False

    def test_wrong_type_returns_false(self):
        task = {"id": "not-int", "title": "t", "status": "pending", "created_at": "2026-06-14 10:00:00", "deadline": None, "priority": "medium"}
        assert is_valid_task(task) is False


class TestConstants:

    def test_status_values(self):
        assert TASK_STATUS_PENDING == "pending"
        assert TASK_STATUS_DONE == "done"

    def test_required_fields_structure(self):
        assert TASK_REQUIRED_FIELDS["id"] == int
        assert TASK_REQUIRED_FIELDS["title"] == str
        assert TASK_REQUIRED_FIELDS["priority"] == str
        for key in ("id", "title", "status", "created_at", "deadline", "priority"):
            assert key in TASK_REQUIRED_FIELDS

    def test_priority_values(self):
        assert PRIORITY_LOW == "low"
        assert PRIORITY_MEDIUM == "medium"
        assert PRIORITY_HIGH == "high"
