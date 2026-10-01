from __future__ import annotations

from datetime import date, datetime, time, timedelta


ROLE_TO_SHIFT = {
    "supervisor": {"supervisor", "valet_day"},
    "valet_day": {"valet_day"},
    "valet_night": {"valet_night"},
}


def _to_datetime(day: str | date, value: str | time, is_end: bool = False) -> datetime:
    if isinstance(day, str):
        day = date.fromisoformat(day)
    if isinstance(value, str):
        value = datetime.strptime(value, "%H:%M").time()
    base = datetime.combine(day, value)
    if is_end and value >= time(0, 0) and value < time(12, 0):
        return base
    return base


def _is_overnight_shift(slot: dict) -> bool:
    return bool(slot.get("is_overnight") or slot.get("role_required") == "valet_night")


def _slot_interval(slot: dict, day: str) -> tuple[datetime, datetime]:
    start = _to_datetime(day, slot["start_time"])
    end = _to_datetime(day, slot["end_time"])
    if _is_overnight_shift(slot):
        end = end + timedelta(days=1)
    return start, end


def _role_matches(user_role: str, slot_role: str) -> bool:
    allowed = ROLE_TO_SHIFT.get(user_role, set())
    return slot_role in allowed or (user_role == "supervisor" and slot_role == "valet_day")


def check_capacity(slot: dict, current_people: int | None = None) -> bool:
    current = slot.get("current_people", 0) if current_people is None else current_people
    return current < slot.get("max_people", 1)


def check_overlap(slot: dict, assignments: list[dict]) -> bool:
    shift_start, shift_end = _slot_interval(slot, slot["date"])
    for entry in assignments:
        if entry.get("role_required") not in {"supervisor", "valet_day", "valet_night"}:
            continue
        candidate_start, candidate_end = _slot_interval(entry, entry["date"])
        if candidate_start < shift_end and shift_start < candidate_end:
            return False
    return True


def check_rest_period(slot: dict, assignments: list[dict], min_rest_hours: int = 10) -> bool:
    slot_start, slot_end = _slot_interval(slot, slot["date"])
    for entry in assignments:
        existing_start, existing_end = _slot_interval(entry, entry["date"])
        if candidate_overlap(slot_start, slot_end, existing_start, existing_end):
            return False

        if slot_start >= existing_end:
            gap = slot_start - existing_end
            if gap < timedelta(hours=min_rest_hours):
                return False

        if existing_start >= slot_end:
            gap = existing_start - slot_end
            if gap < timedelta(hours=min_rest_hours):
                return False
    return True


def candidate_overlap(start_a: datetime, end_a: datetime, start_b: datetime, end_b: datetime) -> bool:
    return start_a < end_b and start_b < end_a


def check_weekly_hours(user_id: str, assignments: list[dict], *, current_duration: int = 0, max_weekly_hours: int = 48) -> bool:
    if not user_id:
        return True
    total = current_duration
    for assignment in assignments:
        if assignment.get("user_id") == user_id:
            total += int(assignment.get("duration_hours", 0))
    return total <= max_weekly_hours


def validate_take(slot: dict, user_role: str, assignments: list[dict], *, min_rest_hours: int = 10, max_weekly_hours: int = 48, user_id: str | None = None) -> tuple[bool, str | None]:
    if not _role_matches(user_role, slot.get("role_required", "")):
        return False, "role_mismatch"
    if not check_capacity(slot):
        return False, "capacity"
    if not check_overlap(slot, assignments):
        return False, "overlap"
    if not check_rest_period(slot, assignments, min_rest_hours=min_rest_hours):
        return False, "rest_period"
    effective_user_id = user_id or slot.get("user_id")
    if effective_user_id:
        current_duration = int(slot.get("duration_hours", 0))
        if not check_weekly_hours(effective_user_id, assignments, current_duration=current_duration, max_weekly_hours=max_weekly_hours):
            return False, "weekly_limit"
    return True, None


def validate_swap(source_assignment: dict, target_user_role: str, assignment_pool: list[dict]) -> tuple[bool, str | None]:
    if source_assignment.get("role_required") != target_user_role:
        return False, "role_mismatch"
    return True, None
