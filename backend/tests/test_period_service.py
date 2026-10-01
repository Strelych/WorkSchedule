from app.services.period_service import build_calendar_days, build_stats


def test_build_calendar_days_has_statuses_for_month():
    days = build_calendar_days(2026, 10)

    assert len(days) > 0
    assert all("date" in day and "status" in day for day in days)


def test_build_stats_reports_totals():
    stats = build_stats(2026, 10)

    assert stats["total_slots"] > 0
    assert "by_role" in stats
    assert "fill_percentage" in stats
