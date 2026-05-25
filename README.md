# AI Construction Assistant

This repository contains a backend API for an AI-powered construction assistant, built using FastAPI.

## Features

- REST API built with FastAPI
- CORS enabled for local frontend development
- Uses SQLAlchemy, psycopg2 for database operations
- Environment variable management with python-dotenv
- OpenAI integration for AI functionality
- Data validation and serialization with Pydantic

## Project Structure

```
backend/
  app/
    main.py         # FastAPI application and routes
    schemas.py      # Pydantic models for request/response data
  requirements.txt  # Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.9+
- [Poetry](https://python-poetry.org/) or `pip`
- PostgreSQL database (if connecting to a real DB)

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <repo-directory>/backend
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup environment variables

Create a `.env` file in `backend` and add:

```
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### 4. Run the API server

```bash
uvicorn app.main:app --reload
```

The server will be available at [http://localhost:8000](http://localhost:8000).

### 5. API Health Check

Access [http://localhost:8000/](http://localhost:8000/) in your browser or use:

```bash
curl http://localhost:8000/
```

You should receive a JSON response indicating the server is running.

---

## License

MIT License.
