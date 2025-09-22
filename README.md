# Todo App (Django + FastAPI)

A full‑stack Todo application that combines a server‑rendered Django UI with a FastAPI REST API, sharing a single SQLite database. Supports task CRUD, search, priorities, due dates, and image uploads. CORS is preconfigured for localhost so React/Vite/Vue/Flutter clients can integrate easily.

## Tech Stack
- Python, Django 5
- FastAPI, Starlette, Pydantic v2
- SQLAlchemy 2, SQLite
- Bootstrap 5 (UI)

## Project Structure
```
./
├── manage.py
├── db.sqlite3
├── README.md
├── requirements.txt
├── .gitignore
├── fastapi_app/
│   ├── main.py          # FastAPI app & routes
│   ├── db.py            # SQLAlchemy engine/session + MEDIA config
│   ├── models.py        # SQLAlchemy model mapped to Django table
│   └── schemas.py       # Pydantic schemas
├── tasks/
│   ├── models.py        # Django Task model
│   ├── views.py         # Django views (index/search/toggle/delete/clear)
│   ├── forms.py         # Django form for task creation
│   ├── urls.py
│   └── templates/tasks/index.html
└── todo_proj/
    ├── settings.py
    └── urls.py
```

## Features
- Web UI (Django) with search, progress bar, and sections for Pending/Completed.
- REST API (FastAPI) for mobile/JS clients.
- Create, list, toggle, delete tasks; clear completed.
- Priority (low/medium/high); optional due date.
- Image uploads stored under `media/task_attachments/`.
- Swagger UI at `/docs` for API exploration.

## API Overview (FastAPI)
Base: `http://127.0.0.1:8001`

- `GET /health` → `{ ok: true }`
- `GET /api/tasks?q=...` → List tasks (optional search by title/description)
- `POST /api/tasks` → Create task (multipart form)
  - Fields: `title` (required), `description?`, `priority?` (`low|medium|high`), `due_date?` (`YYYY-MM-DD`), `image?` (file)
- `POST /api/tasks/{task_id}/toggle` → Toggle `completed`
- `DELETE /api/tasks/{task_id}` → Delete task
- `POST /api/tasks/clear-completed` → Bulk clear completed
- `GET /api/media/{path}` → Optional media proxy (Django also serves `/media/` on port 8000 in DEBUG)

Pydantic schema: `fastapi_app/schemas.py::TaskOut`
SQLAlchemy model: `fastapi_app/models.py::Task` maps to Django table `tasks_task`.

## Local Development

### 1) Create & activate a virtual environment
```powershell
python -m venv env
./env/Scripts/Activate.ps1
```

### 2) Install dependencies
```powershell
pip install -r requirements.txt
```

### 3) Run servers
- Django (UI + media):
```powershell
python manage.py runserver 8000
```
- FastAPI (API):
```powershell
uvicorn fastapi_app.main:app --reload --port 8001
```

### 4) Test the API
- Swagger: http://127.0.0.1:8001/docs
- List tasks: http://127.0.0.1:8001/api/tasks
- Simple HTML form included:
  - Open `api_test.html` in your browser and submit to create a task.

### 5) Frontend integration (React/Vite/Vue/Flutter)
- CORS is enabled for any `localhost`/`127.0.0.1` port in `fastapi_app/main.py`.
- Example fetch:
```js
const res = await fetch('http://127.0.0.1:8001/api/tasks');
const data = await res.json();
```
- For file upload, use `FormData` and POST to `/api/tasks`.

### 6) Media files
- The API returns `image_url` like `/media/...`.
- In development, Django serves media on `http://127.0.0.1:8000/media/...`.
- You can also use `GET /api/media/{path}` from FastAPI.

## Search
- Django UI: Top-right search box submits `q` via GET to `/`.
- FastAPI: `GET /api/tasks?q=keyword`.



## How to Publish to GitHub
1) Create a new repo on GitHub (without a README/.gitignore if you’ll push this existing tree).
2) In the project root:
```bash
git init
git add .
git commit -m "Initial commit: Django + FastAPI Todo app"
# Replace the URL below with your GitHub repo URL
git remote add origin https://github.com/<your-username>/<your-repo>.git
git branch -M main
git push -u origin main
```


