from __future__ import annotations

from datetime import date, time

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.assignment import Assignment, AssignmentStatus
from app.models.planning_period import PlanningPeriod, PlanningPeriodStatus
from app.models.shift_slot import ShiftSlot
from app.models.swap_request import SwapRequest, SwapStatus
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserCreate
from app.services.assignment_checker import validate_take
from app.services.shift_generator import generate_month_slots

router = APIRouter(prefix="/api/bot", tags=["bot"])


def allowed_slot_roles(role: str) -> set[str]:
    if role == "supervisor":
        return {"supervisor", "valet_day"}
    if role == "valet_day":
        return {"valet_day"}
    if role == "valet_night":
        return {"valet_night"}
    return set()


def normalize_role(value: str | None) -> UserRole:
    mapping = {
        "admin": UserRole.ADMIN,
        "supervisor": UserRole.SUPERVISOR,
        "valet_day": UserRole.VALET_DAY,
        "valet_night": UserRole.VALET_NIGHT,
        "day": UserRole.VALET_DAY,
        "night": UserRole.VALET_NIGHT,
    }
    return mapping.get((value or "").lower(), UserRole.VALET_DAY)


class PeriodCreateRequest(BaseModel):
    year: int
    month: int
    admin_user_id: str


class AssignmentTakeRequest(BaseModel):
    slot_id: str
    user_id: str


class SwapCreateRequest(BaseModel):
    assignment_id: str
    user_id: str


class SwapTakeRequest(BaseModel):
    swap_id: str
    user_id: str


class SwapApproveRequest(BaseModel):
    swap_id: str
    admin_user_id: str


@router.post("/users/register")
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.telegram_id == payload.telegram_id).first()
    if existing is not None:
        return {"user_id": existing.id, "status": existing.status.value}

    user = User(
        telegram_id=payload.telegram_id,
        username=payload.username,
        name=payload.name,
        role=normalize_role(payload.role),
        status=UserStatus.PENDING,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"user_id": user.id, "status": user.status.value}


@router.post("/users/approve")
def approve_user(payload: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = UserStatus.ACTIVE
    db.commit()
    return {"status": user.status.value}


@router.get("/users/pending")
def list_pending_users(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.status == UserStatus.PENDING).all()
    return [{
        "id": user.id,
        "telegram_id": user.telegram_id,
        "name": user.name,
        "username": user.username,
        "role": user.role.value,
    } for user in users]


@router.post("/periods/create")
def create_period(payload: PeriodCreateRequest, db: Session = Depends(get_db)):
    if payload.month not in range(1, 13):
        raise HTTPException(status_code=400, detail="Invalid month")

    admin = db.query(User).filter(User.id == payload.admin_user_id).first()
    if admin is None:
        raise HTTPException(status_code=404, detail="Admin user not found")

    period = PlanningPeriod(
        year=payload.year,
        month=payload.month,
        status=PlanningPeriodStatus.DRAFT,
        created_by=payload.admin_user_id,
    )
    db.add(period)
    db.commit()
    db.refresh(period)

    generated = generate_month_slots(payload.year, payload.month)
    slot_records = []
    for slot in generated:
        slot_records.append(
            ShiftSlot(
                period_id=period.id,
                date=date.fromisoformat(slot["date"]),
                shift_type_id=str(slot.get("shift_type_id") or slot.get("shift_name") or slot["role_required"]),
                role_required=slot["role_required"],
                start_time=time.fromisoformat(slot["start_time"]),
                end_time=time.fromisoformat(slot["end_time"]),
                duration_hours=slot["duration_hours"],
                max_people=slot["max_people"],
                current_people=0,
                is_overnight=bool(slot.get("is_overnight", False)),
            )
        )

    db.add_all(slot_records)
    db.commit()
    return {"period_id": period.id, "slots_created": len(slot_records)}


@router.post("/periods/publish")
def publish_period(payload: dict, db: Session = Depends(get_db)):
    period = db.query(PlanningPeriod).filter(PlanningPeriod.id == payload["period_id"]).first()
    if period is None:
        raise HTTPException(status_code=404, detail="Period not found")
    period.status = PlanningPeriodStatus.OPEN
    db.commit()
    return {"status": period.status.value}


@router.get("/slots/available")
def list_available_slots(period_id: str = Query(...), date_filter: str | None = Query(default=None, alias="date"), user_id: str = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    allowed = set(allowed_slot_roles(user.role.value))
    query = db.query(ShiftSlot).filter(ShiftSlot.period_id == period_id, ShiftSlot.role_required.in_(sorted(allowed)))
    if date_filter:
        query = query.filter(ShiftSlot.date == date.fromisoformat(date_filter))

    slots = query.all()
    return [{
        "slot_id": slot.id,
        "shift_name": slot.shift_type_id,
        "start_time": slot.start_time.strftime("%H:%M"),
        "end_time": slot.end_time.strftime("%H:%M"),
        "free_places": max(slot.max_people - slot.current_people, 0),
        "max_people": slot.max_people,
    } for slot in slots]


@router.get("/slots/calendar")
def get_calendar(period_id: str = Query(...), user_id: str = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    allowed = set(allowed_slot_roles(user.role.value))
    slots = db.query(ShiftSlot).filter(ShiftSlot.period_id == period_id, ShiftSlot.role_required.in_(sorted(allowed))).all()

    days: dict[str, dict] = {}
    for slot in slots:
        day_name = slot.date.isoformat()
        entry = days.setdefault(day_name, {"date": day_name, "free_places_total": 0})
        entry["free_places_total"] += max(slot.max_people - slot.current_people, 0)

    entries = [{
        "date": value["date"],
        "status": "green" if value["free_places_total"] > 2 else "yellow" if value["free_places_total"] > 0 else "red",
        "free_places_total": value["free_places_total"],
    } for value in days.values()]
    return {"days": entries}


@router.post("/assignments/take")
def take_assignment(payload: AssignmentTakeRequest, db: Session = Depends(get_db)):
    slot = db.query(ShiftSlot).filter(ShiftSlot.id == payload.slot_id).first()
    if slot is None:
        raise HTTPException(status_code=404, detail="Slot not found")

    user = db.query(User).filter(User.id == payload.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    assignment_records = []
    for assignment in db.query(Assignment).filter(Assignment.user_id == payload.user_id).all():
        assigned_slot = db.query(ShiftSlot).filter(ShiftSlot.id == assignment.slot_id).first()
        if assigned_slot is None:
            continue
        assignment_records.append({
            "date": assigned_slot.date.isoformat(),
            "role_required": assigned_slot.role_required,
            "start_time": assigned_slot.start_time.strftime("%H:%M"),
            "end_time": assigned_slot.end_time.strftime("%H:%M"),
            "duration_hours": assigned_slot.duration_hours,
            "is_overnight": assigned_slot.is_overnight,
            "user_id": assignment.user_id,
        })

    slot_dict = {
        "date": slot.date.isoformat(),
        "role_required": slot.role_required,
        "start_time": slot.start_time.strftime("%H:%M"),
        "end_time": slot.end_time.strftime("%H:%M"),
        "duration_hours": slot.duration_hours,
        "is_overnight": slot.is_overnight,
        "max_people": slot.max_people,
        "current_people": slot.current_people,
    }
    valid, error = validate_take(slot_dict, user.role.value, assignment_records, user_id=payload.user_id)
    if not valid:
        raise HTTPException(status_code=409, detail=error)

    assignment = Assignment(
        slot_id=payload.slot_id,
        user_id=payload.user_id,
        status=AssignmentStatus.SUBMITTED,
    )
    db.add(assignment)
    slot.current_people = min(slot.max_people, slot.current_people + 1)
    db.commit()
    db.refresh(assignment)
    return {"assignment_id": assignment.id, "status": assignment.status.value}


@router.get("/assignments/my")
def my_assignments(user_id: str = Query(...), period_id: str = Query(...), db: Session = Depends(get_db)):
    results = []
    for assignment in db.query(Assignment).filter(Assignment.user_id == user_id).all():
        slot = db.query(ShiftSlot).filter(ShiftSlot.id == assignment.slot_id, ShiftSlot.period_id == period_id).first()
        if slot is None:
            continue
        results.append({
            "assignment_id": assignment.id,
            "date": slot.date.isoformat(),
            "shift_name": slot.shift_type_id,
            "start_time": slot.start_time.strftime("%H:%M"),
            "end_time": slot.end_time.strftime("%H:%M"),
            "status": assignment.status.value,
        })
    return results


@router.post("/swaps/create")
def create_swap(payload: SwapCreateRequest, db: Session = Depends(get_db)):
    assignment = db.query(Assignment).filter(Assignment.id == payload.assignment_id).first()
    if assignment is None:
        raise HTTPException(status_code=404, detail="Assignment not found")

    swap = SwapRequest(
        assignment_id=payload.assignment_id,
        from_user_id=assignment.user_id,
        to_user_id=payload.user_id,
        status=SwapStatus.PENDING,
    )
    db.add(swap)
    db.commit()
    db.refresh(swap)
    return {"swap_id": swap.id, "status": swap.status.value}


@router.post("/swaps/take")
def take_swap(payload: SwapTakeRequest, db: Session = Depends(get_db)):
    swap = db.query(SwapRequest).filter(SwapRequest.id == payload.swap_id).first()
    if swap is None:
        raise HTTPException(status_code=404, detail="Swap not found")

    user = db.query(User).filter(User.id == payload.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    from_user = db.query(User).filter(User.id == swap.from_user_id).first()
    if from_user is None:
        raise HTTPException(status_code=404, detail="Source user not found")
    if user.role != from_user.role:
        raise HTTPException(status_code=403, detail="role_mismatch")

    swap.to_user_id = payload.user_id
    swap.status = SwapStatus.PENDING_APPROVAL
    db.commit()
    return {"status": swap.status.value}


@router.post("/swaps/approve")
def approve_swap(payload: SwapApproveRequest, db: Session = Depends(get_db)):
    swap = db.query(SwapRequest).filter(SwapRequest.id == payload.swap_id).first()
    if swap is None:
        raise HTTPException(status_code=404, detail="Swap not found")
    swap.status = SwapStatus.APPROVED
    db.commit()
    return {"status": swap.status.value}
