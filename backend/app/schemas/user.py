from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    telegram_id: int
    username: str | None = None
    name: str = Field(..., min_length=1)
    role: str


class UserRead(BaseModel):
    id: str
    telegram_id: int
    username: str | None = None
    name: str
    role: str
    status: str = "pending"


class UserUpdate(BaseModel):
    status: str | None = None
