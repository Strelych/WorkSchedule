from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Query

from app.config import settings

router = APIRouter(prefix="/api/web", tags=["website"])


def _require_access_token(x_access_token: str | None):
    if not x_access_token or x_access_token != settings.WEB_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid access token")
    return x_access_token


@router.get("/schedule")
def get_schedule(year: int = Query(...), month: int = Query(...), x_access_token: str | None = Header(default=None)):
    _require_access_token(x_access_token)
    return {
        "period": {"year": year, "month": month, "status": "open"},
        "days": [{
            "date": f"{year}-{month:02d}-01",
            "slots": [{
                "shift_name": "Дневная",
                "role_required": "valet_day",
                "start_time": "09:00",
                "end_time": "21:00",
                "max_people": 2,
                "current_people": 1,
                "employees": [{"name": "Иван", "role": "valet_day"}],
            }],
        }],
    }


@router.get("/stats")
def get_stats(year: int = Query(...), month: int = Query(...), x_access_token: str | None = Header(default=None)):
    _require_access_token(x_access_token)
    return {
        "total_slots": 30,
        "filled_slots": 18,
        "fill_percentage": 60.0,
        "by_role": {
            "supervisor": {"total": 10, "filled": 6},
            "valet_day": {"total": 12, "filled": 7},
            "valet_night": {"total": 8, "filled": 5},
        },
        "problem_days": [{"date": f"{year}-{month:02d}-05", "issues": ["capacity"]}],
        "top_employees": [{"name": "Иван", "role": "valet_day", "hours": 36, "shifts_count": 3}],
    }


@router.get("/employees")
def get_employees(x_access_token: str | None = Header(default=None)):
    _require_access_token(x_access_token)
    return [
        {"id": "user_1", "name": "Иван", "role": "valet_day"},
        {"id": "user_2", "name": "Петр", "role": "supervisor"},
        {"id": "user_3", "name": "Алексей", "role": "valet_night"},
    ]
