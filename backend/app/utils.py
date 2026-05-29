import json

from app.models import Issue
from app.schemas import IssueResponse, IssueAnalysis, TaskRecommendation

def build_issue_response(issue: Issue) -> IssueResponse:
    return IssueResponse(
        id=issue.id,
        title=issue.title,
        description=issue.description,
        project_name=issue.project_name,
        location=issue.location,
        status=issue.status,
        analysis=IssueAnalysis(
            category=issue.category,
            urgency=issue.urgency,
            trade=issue.trade,
            summary=issue.summary,
            next_steps=json.loads(issue.next_steps),
            tasks=[
                TaskRecommendation(**task)
                for task in json.loads(issue.tasks)
            ]
        ),
        analysis_source=issue.analysis_source
    )