import json

import httpx
import pytest
from fastapi.testclient import TestClient
from openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import ai_service
from app.database import Base
from app.main import app, get_db


VALID_ANALYSIS = {
    "category": "Plumbing",
    "urgency": "High",
    "trade": "Plumber",
    "summary": "Water is leaking from a pipe.",
    "next_steps": ["Shut off water", "Inspect pipe", "Call plumber"],
    "tasks": [
        {
            "title": "Inspect pipe",
            "assigned_to": "Site Supervisor",
            "priority": "High"
        }
    ]
}


class FakeOpenAI:
    """Real OpenAI client over a fake transport, so SDK parsing runs for real."""

    def __init__(self):
        self.content = json.dumps(VALID_ANALYSIS)
        self.refusal = None
        self.finish_reason = "stop"
        self.status_code = 200
        self.connection_error = False
        self.requests = []

        self.client = OpenAI(
            api_key="test-key",
            max_retries=0,
            http_client=httpx.Client(transport=httpx.MockTransport(self.handle))
        )

    def handle(self, request):
        self.requests.append(json.loads(request.content))

        if self.connection_error:
            raise httpx.ConnectError("connection refused", request=request)

        if self.status_code != 200:
            return httpx.Response(
                self.status_code,
                json={"error": {"message": "request failed"}}
            )

        return httpx.Response(200, json={
            "id": "chatcmpl-test",
            "object": "chat.completion",
            "created": 0,
            "model": "gpt-4.1-mini",
            "choices": [
                {
                    "index": 0,
                    "finish_reason": self.finish_reason,
                    "message": {
                        "role": "assistant",
                        "content": self.content,
                        "refusal": self.refusal
                    }
                }
            ]
        })

    def set_analysis(self, **fields):
        self.content = json.dumps({**VALID_ANALYSIS, **fields})


# autouse so no test can reach the real OpenAI API
@pytest.fixture(autouse=True)
def fake_openai(monkeypatch):
    fake = FakeOpenAI()
    monkeypatch.setattr(ai_service, "get_client", lambda: fake.client)
    return fake


# each test gets its own in-memory database, never construction_ai.db
@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def make_issue(client):
    def _make_issue(**fields):
        payload = {
            "title": "Leaking pipe",
            "description": "Water leaking from the ceiling",
            "project_name": "Tower A",
            "location": "Level 3",
            **fields
        }
        response = client.post("/issues", json=payload)
        assert response.status_code == 200
        return response.json()

    return _make_issue
