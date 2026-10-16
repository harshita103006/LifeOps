from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AssignmentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    description: str | None = None
    subject: str = Field(min_length=1, max_length=100)
    due_date: datetime
    status: Literal["pending", "in_progress", "completed"] = "pending"


class AssignmentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    subject: str | None = Field(default=None, min_length=1, max_length=100)
    due_date: datetime | None = None
    status: Literal["pending", "in_progress", "completed"] | None = None