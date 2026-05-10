# TaskFlow - Smart Task Management System

A full-stack task management web application built with **Flask**, **PostgreSQL**, **WebSockets**, **Pandas & NumPy**.

---

## Screenshots

<div align="center">
  <img src="screenshots/Screenshot%20(866).png" width="45%" alt="Dashboard" />
  <img src="screenshots/Screenshot%20(865).png" width="45%" alt="Analytics View 1" />
  <img src="screenshots/Screenshot%20(863).png" width="45%" alt="Analytics View 2" />
  <img src="screenshots/Screenshot%20(862).png" width="45%" alt="Registration Page" />
  <img src="screenshots/Screenshot%20(864).png" width="45%" alt="Login Page" />
</div>

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, Flask 3.0 |
| Auth | Flask-Login, Flask-Bcrypt |
| Database | PostgreSQL + SQLAlchemy ORM |
| Analytics | Pandas, NumPy |
| Real-time | WebSockets via Flask-SocketIO |
| Frontend | HTML5, CSS3, Vanilla JS |

---

## Project Structure

```
taskflow/
├── run.py                    # Entry point
├── config.py                 # App configuration
├── requirements.txt          # Python dependencies
├── schema.sql                # Database schema
├── .env.example              # Environment variables template
└── app/
    ├── __init__.py           # App factory
    ├── models.py             # User & Task DB models
    ├── auth.py               # Register / Login / Logout
    ├── tasks.py              # REST API (CRUD)
    ├── analytics.py          # Pandas/NumPy analytics
    ├── websocket.py          # Socket.IO event handlers
    ├── main.py               # Dashboard route
    └── templates/
        ├── base.html         # Base layout + WebSocket JS
        ├── login.html
        ├── register.html
        ├── dashboard.html    # Task list + Add/Edit modal
        └── analytics.html    # Charts and metrics
```

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- PostgreSQL 14+

### 1. Clone and create virtual environment
```bash
git clone <your-repo-url> taskflow
cd taskflow
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up PostgreSQL
```bash
psql -U postgres -c "CREATE DATABASE task_manager;"
```

### 4. Configure environment
```bash
cp .env.example .env
# Open .env and set your DATABASE_URL and SECRET_KEY
```

### 5. Run the application
```bash
python run.py
```

Visit: **http://localhost:5000**

---

## REST API Reference

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | User login |
| GET | `/auth/logout` | Logout |
| GET | `/auth/me` | Current user profile |

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | Get all tasks (supports ?status=, ?priority=, ?sort=, ?order=) |
| POST | `/api/tasks` | Create a new task |
| GET | `/api/tasks/<id>` | Get single task |
| PUT | `/api/tasks/<id>` | Update task |
| DELETE | `/api/tasks/<id>` | Delete task |
| PATCH | `/api/tasks/bulk-status` | Bulk status update |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/summary` | Full analytics (Pandas + NumPy) |

---

## WebSocket Events (namespace: `/tasks`)

| Event (server -> client) | Description |
|--------------------------|-------------|
| `task_created` | Fired when a task is added |
| `task_updated` | Fired when a task is edited |
| `task_deleted` | Fired when a task is deleted |
| `bulk_updated` | Fired on bulk status change |
| `connected` | Confirms WebSocket connection |

---

## Task Model

```json
{
  "id": 1,
  "title": "Complete project report",
  "description": "Write the final summary",
  "priority": "high",
  "status": "in_progress",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T11:00:00",
  "due_date": "2024-01-20T17:00:00",
  "user_id": 1
}
```

**Priority values:** `low`, `medium`, `high`, `urgent`  
**Status values:** `pending`, `in_progress`, `completed`

---

## Analytics Module (Pandas + NumPy)

The `/analytics/summary` endpoint returns:
- Total, completed, pending, in-progress task counts
- Completion percentage (NumPy)
- Priority breakdown per status
- Average tasks created per day (NumPy mean)
- Tasks completed in last 7 days
- Standard deviation of daily task creation (NumPy std)
- Priority-wise completion rates
- Task creation timeline data

---

## Features

- **Authentication** - Secure register/login/logout with bcrypt password hashing
- **REST API** - Full CRUD for tasks with filtering, sorting, and bulk operations
- **PostgreSQL** - Properly normalized schema with indexes
- **Analytics** - Real Pandas DataFrame processing + NumPy statistical functions
- **WebSockets** - Live toast notifications on any task change
- **Responsive UI** - Dark-themed, clean, mobile-friendly interface
