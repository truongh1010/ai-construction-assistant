import json

import pytest

from app import ai_service
from app.ai_service import fake_ai_analyze_issue
from app.schemas import IssueCreate
from tests.conftest import VALID_ANALYSIS


real_get_client = ai_service.get_client


def without(field):
    return {key: value for key, value in VALID_ANALYSIS.items() if key != field}


def server_error(fake):
    fake.status_code = 500


def rate_limited(fake):
    fake.status_code = 429


def bad_api_key(fake):
    fake.status_code = 401


def connection_error(fake):
    fake.connection_error = True


def refusal(fake):
    fake.content = None
    fake.refusal = "I can't help with that."


def truncated(fake):
    fake.finish_reason = "length"


def content_filtered(fake):
    fake.finish_reason = "content_filter"


def not_json(fake):
    fake.content = "Here is the analysis: it looks bad."


def markdown_fenced(fake):
    fake.content = f"```json\n{json.dumps(VALID_ANALYSIS)}\n```"


def urgency_out_of_range(fake):
    fake.set_analysis(urgency="Urgent")


def urgency_wrong_case(fake):
    fake.set_analysis(urgency="high")


def priority_out_of_range(fake):
    fake.set_analysis(
        tasks=[{"title": "T", "assigned_to": "A", "priority": "ASAP"}]
    )


def missing_field(fake):
    fake.content = json.dumps(without("urgency"))


FAILURES = [
    server_error,
    rate_limited,
    bad_api_key,
    connection_error,
    refusal,
    truncated,
    content_filtered,
    not_json,
    markdown_fenced,
    urgency_out_of_range,
    urgency_wrong_case,
    priority_out_of_range,
    missing_field
]


@pytest.mark.parametrize("failure", FAILURES)
def test_create_issue_falls_back_when_openai_fails(client, make_issue, fake_openai, failure):
    failure(fake_openai)

    issue = make_issue(description="Water leaking from a pipe")

    assert issue["analysis_source"] == "fallback"
    assert issue["analysis"]["category"] == "Plumbing"
    assert client.get(f"/issues/{issue['id']}").json() == issue


@pytest.mark.parametrize("failure", FAILURES)
def test_reanalyze_falls_back_when_openai_fails(client, make_issue, fake_openai, failure):
    issue = make_issue(description="Water leaking from a pipe")
    failure(fake_openai)

    response = client.post(f"/issues/{issue['id']}/reanalyze")

    assert response.status_code == 200
    assert response.json()["analysis_source"] == "fallback"


def test_reanalyze_returns_to_openai_after_recovery(client, make_issue, fake_openai):
    fake_openai.status_code = 500
    issue = make_issue()
    fake_openai.status_code = 200

    response = client.post(f"/issues/{issue['id']}/reanalyze")

    assert response.json()["analysis_source"] == "openai"


def test_missing_api_key_falls_back(make_issue, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(ai_service, "get_client", real_get_client)
    real_get_client.cache_clear()

    issue = make_issue()

    assert issue["analysis_source"] == "fallback"


def test_request_constrains_model_to_schema(make_issue, fake_openai):
    make_issue()

    response_format = fake_openai.requests[-1]["response_format"]
    schema = response_format["json_schema"]["schema"]
    allowed = ["Low", "Medium", "High", "Critical"]

    assert response_format["type"] == "json_schema"
    assert response_format["json_schema"]["strict"] is True
    assert schema["properties"]["urgency"]["enum"] == allowed
    assert schema["$defs"]["TaskRecommendation"]["properties"]["priority"]["enum"] == allowed


@pytest.mark.parametrize("description, category, urgency, trade", [
    ("Steel delivery is delayed", "Schedule", "High", "Project Management"),
    ("Change will exceed the budget", "Budget", "Medium", "Project Management"),
    ("Exposed rebar hazard", "Safety", "Critical", "Site Safety"),
    ("Burst pipe in basement", "Plumbing", "High", "Plumber"),
    ("Exposed wire in panel", "Electrical", "High", "Electrician"),
    ("Paint color question", "General", "Medium", "General Contractor")
])
def test_fallback_keyword_rules(description, category, urgency, trade):
    analysis = fake_ai_analyze_issue(
        IssueCreate(title="Issue", description=description)
    )

    assert analysis.category == category
    assert analysis.urgency == urgency
    assert analysis.trade == trade
    assert analysis.tasks
