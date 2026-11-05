# AI Construction Assistant

A full-stack construction issue tracker with AI-powered analysis. Submit site issues from a React dashboard, get category/urgency/trade classification plus next steps and recommended tasks, then manage issues over their lifecycle.

## Features

### Frontend (React + Vite)

- Construction issue submission form with live AI analysis results
- Dashboard stats: total, open, in progress, resolved, and high/critical urgency counts
- Issue list with search, status filters, and sorting (newest, oldest, urgency, status)
- Per-issue actions: edit details, change status, reanalyze with AI, delete
- Debounced search and server-driven filtering/sorting via query parameters
- Responsive layout styled with `App.css`

### Backend (FastAPI)

- REST API for issue CRUD and workflow operations
- SQLite database (local file: `backend/construction_ai.db`)
- OpenAI-powered analysis using Structured Outputs, so the model is constrained to the `IssueAnalysis` schema
- Automatic fallback to rule-based analysis when the API is unavailable or returns an unusable response
- CORS enabled for the Vite dev server (`http://localhost:5173`, `http://127.0.0.1:5173`)
- Pydantic schemas for request/response validation, with `Literal` types restricting urgency, priority, and status to fixed values
- pytest suite covering the endpoints and the fallback path

### AI analysis output

Each issue receives:

- **Category** (e.g. Plumbing, Safety, Schedule)
- **Urgency** (Low, Medium, High, Critical)
- **Trade** (responsible trade or role)
- **Summary**
- **Next steps** (action list)
- **Recommended tasks** (title, assignee, priority)

## Project structure

```
AI-construction-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI routes
│   │   ├── models.py        # SQLAlchemy Issue model
│   │   ├── schemas.py       # Pydantic models
│   │   ├── database.py      # SQLite engine and session
│   │   ├── ai_service.py    # OpenAI + fallback analysis
│   │   └── utils.py         # Response helpers
│   ├── tests/               # pytest suite (no API key or network needed)
│   ├── requirements.txt
│   ├── requirements-dev.txt # requirements.txt + pytest
│   └── .env                 # OPENAI_API_KEY (not committed)
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── api/issues.js    # Axios API client
│   │   └── components/
│   │       ├── IssueForm.jsx
│   │       ├── IssueList.jsx
│   │       └── DashBoardStats.jsx
│   └── package.json
└── README.md
```

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/issues` | Create issue and run AI analysis |
| `GET` | `/issues` | List issues (`status`, `search`, `sort_by` query params) |
| `GET` | `/issues/{id}` | Get one issue |
| `PUT` | `/issues/{id}` | Update issue title, description, project, location |
| `PATCH` | `/issues/{id}/status` | Update status (`Open`, `In Progress`, `Resolved`; anything else returns `422`) |
| `POST` | `/issues/{id}/reanalyze` | Re-run AI analysis on existing issue |
| `DELETE` | `/issues/{id}` | Delete issue |

### Query parameters for `GET /issues`

| Param | Values | Description |
|-------|--------|-------------|
| `status` | `Open`, `In Progress`, `Resolved` | Filter by status (omit for all) |
| `search` | string | Case-insensitive search across title, description, project, location, status, and analysis fields |
| `sort_by` | `newest`, `oldest`, `urgency`, `status` | Sort order (default: `newest`) |

## Getting started

### Prerequisites

- Python 3.9+
- Node.js 18+ and npm

### 1. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

> **Note:** If `OPENAI_API_KEY` is missing or the API call fails, the backend falls back to rule-based analysis in `ai_service.py` so the app still works locally.

Start the API:

```bash
uvicorn app.main:app --reload
```

API: [http://127.0.0.1:8000](http://127.0.0.1:8000)  
Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Frontend setup

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

App: [http://localhost:5173](http://localhost:5173)

The frontend calls the API at `http://127.0.0.1:8000` (see `frontend/src/api/issues.js`). Change `API_BASE_URL` there if your backend runs on a different host or port.

### 3. Verify

1. Open the frontend in your browser.
2. Submit a construction issue (title + description required).
3. Confirm AI analysis appears and the issue shows in the saved issues panel.
4. Try filtering, searching, editing, changing status, reanalyzing, and deleting.

## Testing

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

Tests use FastAPI's `TestClient` with an in-memory SQLite database, so `construction_ai.db` is never touched. OpenAI calls go through the real SDK over a fake HTTP transport, so response parsing and schema validation run for real without an API key or network access.

## Tech stack

| Layer | Technologies |
|-------|----------------|
| Frontend | React 19, Vite, Axios |
| Backend | FastAPI, SQLAlchemy, Pydantic, Uvicorn |
| Database | SQLite |
| AI | OpenAI API (`gpt-4.1-mini`) with Structured Outputs and keyword-based fallback |
| Testing | pytest, FastAPI TestClient |

## Development notes

- The SQLite database file is created automatically on first run (`construction_ai.db` in `backend/`).
- Backend `.env` and `*.db` are gitignored; do not commit secrets or local DB files.
- Frontend components use **4-space** indentation.
