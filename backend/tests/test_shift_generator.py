from app.services.shift_generator import generate_month_slots


def test_generate_month_slots_creates_expected_count_for_october_2026():
    slots = generate_month_slots(2026, 10)

    assert len(slots) > 0
    assert any(slot["role_required"] == "supervisor" for slot in slots)
    assert any(slot["role_required"] == "valet_night" for slot in slots)
    assert any(slot["is_overnight"] is True for slot in slots)


def test_generate_month_slots_keeps_shift_names_and_capacity():
    slots = generate_month_slots(2026, 10)
    first = slots[0]

    assert "shift_name" in first
    assert "max_people" in first
    assert first["max_people"] > 0
