from app.services.assignment_checker import validate_take


def test_overlap_is_blocked():
    slot = {"date": "2026-10-01", "role_required": "valet_day", "start_time": "09:00", "end_time": "21:00", "max_people": 2, "current_people": 1, "duration_hours": 12, "is_overnight": False}
    assignments = [{
        "date": "2026-10-01",
        "role_required": "valet_day",
        "start_time": "10:00",
        "end_time": "18:00",
        "duration_hours": 8,
        "is_overnight": False,
    }]

    valid, error = validate_take(slot, "valet_day", assignments, min_rest_hours=10, max_weekly_hours=48)
    assert valid is False
    assert error == "overlap"


def test_capacity_is_blocked():
    slot = {"date": "2026-10-02", "role_required": "supervisor", "start_time": "08:00", "end_time": "16:00", "max_people": 1, "current_people": 1, "duration_hours": 8, "is_overnight": False}
    valid, error = validate_take(slot, "supervisor", [], min_rest_hours=10, max_weekly_hours=48)
    assert valid is False
    assert error == "capacity"


def test_night_shift_blocks_next_morning_shift():
    slot = {"date": "2026-10-02", "role_required": "supervisor", "start_time": "08:00", "end_time": "16:00", "max_people": 2, "current_people": 0, "duration_hours": 8, "is_overnight": False}
    assignments = [{
        "date": "2026-10-01",
        "role_required": "valet_night",
        "start_time": "21:00",
        "end_time": "09:00",
        "duration_hours": 12,
        "is_overnight": True,
    }]

    valid, error = validate_take(slot, "supervisor", assignments, min_rest_hours=10, max_weekly_hours=48)
    assert valid is False
    assert error == "overlap"


def test_weekly_limit_is_blocked():
    slot = {"date": "2026-10-03", "role_required": "valet_day", "start_time": "09:00", "end_time": "21:00", "max_people": 2, "current_people": 0, "duration_hours": 12, "is_overnight": False, "user_id": "u-1"}
    assignments = [{"user_id": "u-1", "date": "2026-10-04", "role_required": "valet_day", "start_time": "09:00", "end_time": "21:00", "duration_hours": 48, "is_overnight": False}]
    valid, error = validate_take(slot, "valet_day", assignments, min_rest_hours=10, max_weekly_hours=48)
    assert valid is False
    assert error == "weekly_limit"


def test_role_mismatch_is_blocked():
    slot = {"date": "2026-10-04", "role_required": "valet_night", "start_time": "21:00", "end_time": "09:00", "max_people": 2, "current_people": 0, "duration_hours": 12, "is_overnight": True}
    valid, error = validate_take(slot, "valet_day", [], min_rest_hours=10, max_weekly_hours=48)
    assert valid is False
    assert error == "role_mismatch"
