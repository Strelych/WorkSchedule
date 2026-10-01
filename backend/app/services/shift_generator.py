from __future__ import annotations

from datetime import date, timedelta

from app.utils.config_loader import load_shifts_config


def _month_days(year: int, month: int) -> list[date]:
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    current = date(year, month, 1)
    days: list[date] = []
    while current < next_month:
        days.append(current)
        current += timedelta(days=1)
    return days


def _build_shift_lookup(config: dict) -> dict[str, dict]:
    lookup: dict[str, dict] = {}
    for role_name, role_info in config.get("roles", {}).items():
        for shift in role_info.get("shifts", []):
            lookup[shift["id"]] = {**shift, "role_required": role_name}
    return lookup


def generate_month_slots(year: int, month: int, config: dict | None = None) -> list[dict]:
    config = config or load_shifts_config()
    templates = config.get("generation_rules", {}).get("daily_template", [])
    shift_lookup = _build_shift_lookup(config)

    slots: list[dict] = []
    for day in _month_days(year, month):
        for template in templates:
            role_name = template["role"]
            for shift_id in template.get("shift_ids", []):
                source = shift_lookup.get(shift_id)
                if source is None:
                    continue
                slot = {
                    "date": day.isoformat(),
                    "shift_type_id": shift_id,
                    "role_required": role_name,
                    "shift_name": source["name"],
                    "start_time": source["start_time"],
                    "end_time": source["end_time"],
                    "duration_hours": int(source["duration_hours"]),
                    "max_people": int(source.get("default_capacity", 1)),
                    "current_people": 0,
                    "is_overnight": bool(source.get("is_overnight", False)),
                }
                slots.append(slot)
    return slots
