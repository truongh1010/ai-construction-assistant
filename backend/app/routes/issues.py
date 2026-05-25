from asyncio import tasks
from fastapi import APIRouter
from app.schemas import IssueCreate, IssueAnalysis, TaskRecommendation

router = APIRouter(
    prefix="/issues",
    tags=["Issues"]
)

@router.post("/analyze", response_model=IssueAnalysis)
def analyze_issue(issue: IssueCreate):
    return IssueAnalysis(
        category="Water Damage / Plumbing",
        urgency="High",
        trade="Plumber",
        summary=f"Potential construction issue reported: {issue.title}",
        next_steps=[
            "Document the issue with photos.",
            "Notify the site manager or responsible supervisor.",
            "Inspect the affected area for safety risks.",
            "Assign the appropriate trade for follow-up."
        ],
        tasks=[
            TaskRecommendation(
                title="Review submitted issue details",
                assigned_to="Site Manager",
                priority="High"
            ),
            TaskRecommendation(
                title="Inspect affected location",
                assigned_to="Field Supervisor",
                priority="High"
            ),
            TaskRecommendation(
                title="Create repair plan",
                assigned_to="Responsible Trade",
                priority="Medium"
            )
        ]
    )