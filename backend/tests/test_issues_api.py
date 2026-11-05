import pytest


def test_health_check(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# POST /issues

def test_create_issue_stores_openai_analysis(client, make_issue):
    issue = make_issue()

    assert issue["status"] == "Open"
    assert issue["analysis_source"] == "openai"
    assert issue["analysis"]["urgency"] == "High"
    assert issue["analysis"]["tasks"][0]["assigned_to"] == "Site Supervisor"
    assert client.get(f"/issues/{issue['id']}").json() == issue


@pytest.mark.parametrize("payload", [
    {"title": "No description"},
    {"description": "No title"},
    {}
])
def test_create_issue_requires_title_and_description(client, payload):
    assert client.post("/issues", json=payload).status_code == 422


def test_create_issue_optional_fields_can_be_omitted(client):
    response = client.post("/issues", json={"title": "A", "description": "B"})

    assert response.status_code == 200
    assert response.json()["project_name"] is None
    assert response.json()["location"] is None


# GET /issues

def test_list_issues_empty(client):
    assert client.get("/issues").json() == []


def titles(response):
    return [issue["title"] for issue in response.json()]


def test_list_issues_sorted_newest_first_by_default(client, make_issue):
    make_issue(title="First")
    make_issue(title="Second")

    assert titles(client.get("/issues")) == ["Second", "First"]


def test_list_issues_sort_oldest(client, make_issue):
    make_issue(title="First")
    make_issue(title="Second")

    response = client.get("/issues", params={"sort_by": "oldest"})

    assert titles(response) == ["First", "Second"]


def test_list_issues_sort_urgency(client, make_issue, fake_openai):
    for urgency in ["Medium", "Critical", "Low", "High"]:
        fake_openai.set_analysis(urgency=urgency)
        make_issue(title=urgency)

    response = client.get("/issues", params={"sort_by": "urgency"})

    assert titles(response) == ["Critical", "High", "Medium", "Low"]


def test_list_issues_sort_status(client, make_issue):
    resolved = make_issue(title="Resolved one")
    make_issue(title="Open one")
    client.patch(f"/issues/{resolved['id']}/status", json={"status": "Resolved"})

    response = client.get("/issues", params={"sort_by": "status"})

    assert titles(response) == ["Open one", "Resolved one"]


def test_list_issues_filter_by_status(client, make_issue):
    in_progress = make_issue(title="Started")
    make_issue(title="Not started")
    client.patch(f"/issues/{in_progress['id']}/status", json={"status": "In Progress"})

    response = client.get("/issues", params={"status": "In Progress"})

    assert titles(response) == ["Started"]


def test_list_issues_status_all_returns_everything(client, make_issue):
    make_issue()
    make_issue()

    assert len(client.get("/issues", params={"status": "All"}).json()) == 2


@pytest.mark.parametrize("term", ["TOWER b", "basement", "sump"])
def test_list_issues_search_is_case_insensitive_across_fields(client, make_issue, term):
    make_issue(
        title="Sump pump failure",
        project_name="Tower B",
        location="Basement"
    )
    make_issue(title="Other", project_name="Tower A", location="Roof")

    response = client.get("/issues", params={"search": term})

    assert titles(response) == ["Sump pump failure"]


def test_list_issues_search_covers_analysis_fields(client, make_issue, fake_openai):
    fake_openai.set_analysis(trade="Glazier")
    make_issue(title="Cracked window")
    fake_openai.set_analysis(trade="Plumber")
    make_issue(title="Leak")

    response = client.get("/issues", params={"search": "glazier"})

    assert titles(response) == ["Cracked window"]


# GET /issues/{id}

def test_get_issue_not_found(client):
    assert client.get("/issues/999").status_code == 404


# PUT /issues/{id}

def test_update_issue_changes_only_provided_fields(client, make_issue):
    issue = make_issue()

    response = client.put(f"/issues/{issue['id']}", json={"title": "New title"})

    assert response.status_code == 200
    assert response.json()["title"] == "New title"
    assert response.json()["description"] == issue["description"]
    assert response.json()["analysis"] == issue["analysis"]


def test_update_issue_not_found(client):
    assert client.put("/issues/999", json={"title": "X"}).status_code == 404


# PATCH /issues/{id}/status

@pytest.mark.parametrize("status", ["Open", "In Progress", "Resolved"])
def test_update_status_accepts_allowed_values(client, make_issue, status):
    issue = make_issue()

    response = client.patch(f"/issues/{issue['id']}/status", json={"status": status})

    assert response.status_code == 200
    assert response.json()["status"] == status


@pytest.mark.parametrize("status", ["Done", "In progress", "open", "", None])
def test_update_status_rejects_other_values(client, make_issue, status):
    issue = make_issue()

    response = client.patch(f"/issues/{issue['id']}/status", json={"status": status})

    assert response.status_code == 422
    assert client.get(f"/issues/{issue['id']}").json()["status"] == "Open"


def test_update_status_not_found(client):
    response = client.patch("/issues/999/status", json={"status": "Open"})

    assert response.status_code == 404


# DELETE /issues/{id}

def test_delete_issue(client, make_issue):
    issue = make_issue()

    assert client.delete(f"/issues/{issue['id']}").status_code == 200
    assert client.get(f"/issues/{issue['id']}").status_code == 404


def test_delete_issue_not_found(client):
    assert client.delete("/issues/999").status_code == 404


# POST /issues/{id}/reanalyze

def test_reanalyze_replaces_analysis_and_keeps_status(client, make_issue, fake_openai):
    issue = make_issue()
    client.patch(f"/issues/{issue['id']}/status", json={"status": "In Progress"})
    fake_openai.set_analysis(urgency="Critical", category="Structural")

    response = client.post(f"/issues/{issue['id']}/reanalyze")

    assert response.status_code == 200
    assert response.json()["analysis"]["urgency"] == "Critical"
    assert response.json()["analysis"]["category"] == "Structural"
    assert response.json()["status"] == "In Progress"


def test_reanalyze_uses_edited_issue_text(client, make_issue, fake_openai):
    issue = make_issue()
    client.put(f"/issues/{issue['id']}", json={"description": "Scaffold collapsed"})

    client.post(f"/issues/{issue['id']}/reanalyze")

    assert "Scaffold collapsed" in fake_openai.requests[-1]["messages"][1]["content"]


def test_reanalyze_not_found(client):
    assert client.post("/issues/999/reanalyze").status_code == 404
