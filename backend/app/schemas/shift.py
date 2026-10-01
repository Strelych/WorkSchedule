from pydantic import BaseModel


class ShiftSlotCreate(BaseModel):
    period_id: str
    date: str
    shift_type_id: str
    role_required: str
    start_time: str
    end_time: str
    duration_hours: int
    max_people: int
    is_overnight: bool = False


class ShiftSlotRead(BaseModel):
    slot_id: str
    shift_name: str
    start_time: str
    end_time: str
    free_places: int
    max_people: int
