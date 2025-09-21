from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from sqlalchemy.sql import func
from .db import Base

# Reflect Django 'tasks_task' table structure
class Task(Base):
    __tablename__ = 'tasks_task'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, nullable=False, default=False)
    image = Column(String, nullable=True)  # stores relative path like 'task_attachments/xyz.png'
    priority = Column(String(10), nullable=True)  # 'low' | 'medium' | 'high'
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
