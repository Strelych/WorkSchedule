from __future__ import annotations

from collections import defaultdict

from app.services.shift_generator import generate_month_slots


def summarize_day_status(slots: list[dict], *, user_role: str | None = None) -> str:
    relevant = slots
    if user_role:
        allowed = {"supervisor": {"supervisor", "valet_day"}, "valet_day": {"valet_day"}, "valet_night": {"valet_night"}}
        relevant = [slot for slot in slots if slot.get("role_required") in allowed.get(user_role, set())]

    if not relevant:
        return "black"
    free_total = sum(max(int(slot.get("max_people", 0)) - int(slot.get("current_people", 0)), 0) for slot in relevant)
    if free_total >= 4:
        return "green"
    if free_total > 0:
        return "yellow"
    return "red"


def build_calendar_days(year: int, month: int, *, user_role: str | None = None) -> list[dict]:
    slots = generate_month_slots(year, month)
    grouped: dict[str, list[dict]] = defaultdict(list)
    for slot in slots:
        grouped[slot["date"]].append(slot)

    days: list[dict] = []
    for day in sorted(grouped):
        relevant = grouped[day]
        free_total = sum(max(int(slot.get("max_people", 0)) - int(slot.get("current_people", 0)), 0) for slot in relevant)
        if user_role:
            allowed = {"supervisor": {"supervisor", "valet_day"}, "valet_day": {"valet_day"}, "valet_night": {"valet_night"}}
            relevant = [slot for slot in relevant if slot.get("role_required") in allowed.get(user_role, set())]
            free_total = sum(max(int(slot.get("max_people", 0)) - int(slot.get("current_people", 0)), 0) for slot in relevant)
        days.append({
            "date": day,
            "status": summarize_day_status(relevant, user_role=user_role),
            "free_places_total": free_total,
            "slots": relevant,
        })
    return days


def build_stats(year: int, month: int) -> dict:
    slots = generate_month_slots(year, month)
    totals = {"supervisor": 0, "valet_day": 0, "valet_night": 0}
    filled = {"supervisor": 0, "valet_day": 0, "valet_night": 0}

    for slot in slots:
        role = slot.get("role_required")
        totals[role] = totals.get(role, 0) + 1
        if slot.get("current_people", 0) >= slot.get("max_people", 0):
            filled[role] = filled.get(role, 0) + 1

    total_slots = len(slots)
    filled_slots = sum(1 for slot in slots if slot.get("current_people", 0) >= slot.get("max_people", 0))
    fill_percentage = round((filled_slots / total_slots) * 100, 2) if total_slots else 0.0

    return {
        "total_slots": total_slots,
        "filled_slots": filled_slots,
        "fill_percentage": fill_percentage,
        "by_role": {
            key: {"total": totals.get(key, 0), "filled": filled.get(key, 0)} for key in ["supervisor", "valet_day", "valet_night"]
        },
        "problem_days": [],
        "top_employees": [],
    }
