from pathlib import Path
from typing import List, Optional
from datetime import date
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
import shutil
import uuid

from .db import get_db, MEDIA_ROOT, MEDIA_URL
from .models import Task
from .schemas import TaskOut

app = FastAPI(title="Todo FastAPI", version="1.0.0")

# If you will call from other origins later, adjust this
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    # Allow any localhost/127.0.0.1 port during development (e.g., 3000, 5173, 8080, etc.)
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\\d+)?$",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Return JSON for unexpected errors so the UI can show a helpful message
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    # Avoid leaking internals in production; fine for local dev
    return JSONResponse(status_code=500, content={"detail": str(exc) or "Internal Server Error"})

# ---------- Utilities ----------

def _image_url(rel_path: Optional[str]) -> Optional[str]:
    if not rel_path:
        return None
    # Return a path that Django is already serving at /media/
    return f"{MEDIA_URL}{rel_path}".replace("//", "/")


def _task_to_schema(t: Task) -> TaskOut:
    return TaskOut(
        id=t.id,
        title=t.title,
        description=t.description,
        completed=t.completed,
        image_url=_image_url(t.image),
        priority=t.priority,
        due_date=t.due_date.isoformat() if t.due_date else None,
        created_at=t.created_at,
        updated_at=t.updated_at,
    )


def _save_upload(file: UploadFile) -> str:
    # Save to MEDIA_ROOT / task_attachments / unique filename
    ext = Path(file.filename).suffix or ""
    unique = f"{uuid.uuid4().hex}{ext}"
    target_dir = MEDIA_ROOT / "task_attachments"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / unique
    with target_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Return relative path stored in DB
    return f"task_attachments/{unique}"

# ---------- Routes ----------

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/api/tasks", response_model=List[TaskOut])
def list_tasks(db: Session = Depends(get_db), q: str = ""):
    qs = db.query(Task)
    if q:
        like = f"%{q}%"
        qs = qs.filter((Task.title.ilike(like)) | (Task.description.ilike(like)))
    qs = qs.order_by(Task.created_at.desc())
    return [_task_to_schema(t) for t in qs.all()]


@app.post("/api/tasks", response_model=TaskOut)
async def create_task(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    priority: Optional[str] = Form(None),
    due_date: Optional[str] = Form(None),  # YYYY-MM-DD
    db: Session = Depends(get_db),
):
    rel_image: Optional[str] = None
    if image is not None and image.filename:
        rel_image = _save_upload(image)
    parsed_due: Optional[date] = None
    if due_date:
        try:
            parsed_due = date.fromisoformat(due_date)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid due_date format. Use YYYY-MM-DD.")

    # normalize priority
    if priority:
        p = priority.lower()
        if p not in ("low", "medium", "high"):
            raise HTTPException(status_code=422, detail="Invalid priority. Use low|medium|high.")
        priority = p

    t = Task(
        title=title,
        description=description,
        completed=False,
        image=rel_image,
        priority=priority,
        due_date=parsed_due,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return _task_to_schema(t)


@app.post("/api/tasks/{task_id}/toggle", response_model=TaskOut)
def toggle_task(task_id: int, db: Session = Depends(get_db)):
    t: Task = db.query(Task).get(task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    t.completed = not t.completed
    t.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(t)
    return _task_to_schema(t)


@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    t: Task = db.query(Task).get(task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(t)
    db.commit()
    return {"ok": True}


@app.post("/api/tasks/clear-completed")
def clear_completed(db: Session = Depends(get_db)):
    count = db.query(Task).filter(Task.completed.is_(True)).count()
    db.query(Task).filter(Task.completed.is_(True)).delete(synchronize_session=False)
    db.commit()
    return {"cleared": count}


# Optional route to serve a file directly via FastAPI (not required since Django serves /media)
@app.get("/api/media/{path:path}")
def serve_media(path: str):
    file_path = MEDIA_ROOT / path
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(file_path))
