from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = None  # 'low' | 'medium' | 'high'
    due_date: Optional[str] = None  # ISO date string 'YYYY-MM-DD'

class TaskCreate(TaskBase):
    pass

class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    image_url: Optional[str]
    priority: Optional[str]
    due_date: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
