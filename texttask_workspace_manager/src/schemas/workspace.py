from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class WorkspaceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, example="My Team")
    description: Optional[str] = Field(None, max_length=500)


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceUpdate(WorkspaceBase):
    name: Optional[str] = None
    description: Optional[str] = None


class WorkspaceRead(WorkspaceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True