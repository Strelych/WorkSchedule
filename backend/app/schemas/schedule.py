from pydantic import BaseModel


class ScheduleEmployee(BaseModel):
    name: str
    role: str


class ScheduleSlot(BaseModel):
    shift_name: str
    role_required: str
    start_time: str
    end_time: str
    max_people: int
    current_people: int
    employees: list[ScheduleEmployee]


class ScheduleDay(BaseModel):
    date: str
    slots: list[ScheduleSlot]


class ScheduleResponse(BaseModel):
    period: dict
    days: list[ScheduleDay]


class StatsResponse(BaseModel):
    total_slots: int
    filled_slots: int
    fill_percentage: float
    by_role: dict
    problem_days: list[dict]
    top_employees: list[dict]
