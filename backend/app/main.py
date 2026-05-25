import json
from nis import cat

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routes import issues

from sqlalchemy.orm import Session, session
from app.models import Issue
from app.schemas import IssueAnalysis, IssueCreate, IssueResponse, TaskRecommendation
from app.database import Base, engine, SessionLocal

app = FastAPI(title="AI Construction Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# register issues router in FastAPI
app.include_router(issues.router)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def fake_ai_analyze_issue(issue: IssueCreate) -> IssueAnalysis:
    description = issue.description.lower()

    if "delay" in description or "late" in description or "schedule" in description:
        category = "Schedule"
        urgency = "High"
        trade = "Project Management"
        summary = f"The issue '{issue.title}' appears to affect the project schedule."
        next_steps = [
            "Review the current project schedule",
            "Identify the delayed activity or dependency",
            "Contact the responsible subcontractor or supplier",
            "Update stakeholders about the possible schedule impact"
        ]
        tasks = [
            TaskRecommendation(
                title="Review project schedule impact",
                assigned_to="Project Manager",
                priority="High"
            ),
            TaskRecommendation(
                title="Follow up with responsible party",
                assigned_to="Site Supervisor",
                priority="High"
            )
        ]

    elif "cost" in description or "budget" in description or "expensive" in description:
        category = "Budget"
        urgency = "Medium"
        trade = "Project Management"
        summary = f"The issue '{issue.title}' appears to involve a budget or cost concern."
        next_steps = [
            "Review the original budget",
            "Estimate the cost impact",
            "Document the reason for the cost change",
            "Prepare a change order if needed"
        ]
        tasks = [
            TaskRecommendation(
                title="Estimate cost impact",
                assigned_to="Project Manager",
                priority="Medium"
            ),
            TaskRecommendation(
                title="Prepare change order draft",
                assigned_to="Project Coordinator",
                priority="Medium"
            )
        ]

    elif "safety" in description or "hazard" in description or "injury" in description:
        category = "Safety"
        urgency = "Critical"
        trade = "Site Safety"
        summary = f"The issue '{issue.title}' appears to involve a safety risk that needs immediate attention."
        next_steps = [
            "Secure the affected area",
            "Stop related work if necessary",
            "Notify the site supervisor immediately",
            "Document the safety concern and assign corrective action"
        ]
        tasks = [
            TaskRecommendation(
                title="Secure affected area",
                assigned_to="Site Supervisor",
                priority="Critical"
            ),
            TaskRecommendation(
                title="Document safety issue",
                assigned_to="Safety Officer",
                priority="Critical"
            )
        ]

    elif "leak" in description or "water" in description or "pipe" in description:
        category = "Plumbing"
        urgency = "High"
        trade = "Plumber"
        summary = f"The issue '{issue.title}' appears to involve a plumbing problem that may require quick inspection."
        next_steps = [
            "Inspect the affected area",
            "Identify the source of the leak or water issue",
            "Contact the plumbing subcontractor",
            "Document photos and update the issue log"
        ]
        tasks = [
            TaskRecommendation(
                title="Inspect water issue on site",
                assigned_to="Site Supervisor",
                priority="High"
            ),
            TaskRecommendation(
                title="Contact plumbing subcontractor",
                assigned_to="Project Manager",
                priority="High"
            )
        ]

    elif "electrical" in description or "power" in description or "wire" in description:
        category = "Electrical"
        urgency = "High"
        trade = "Electrician"
        summary = f"The issue '{issue.title}' appears to involve electrical work and should be reviewed for safety."
        next_steps = [
            "Stop work in the affected area if unsafe",
            "Inspect the electrical issue",
            "Notify the electrical subcontractor",
            "Verify work meets safety requirements"
        ]
        tasks = [
            TaskRecommendation(
                title="Inspect electrical issue",
                assigned_to="Electrician",
                priority="High"
            ),
            TaskRecommendation(
                title="Verify site safety",
                assigned_to="Site Supervisor",
                priority="High"
            )
        ]

    else:
        category = "General"
        urgency = "Medium"
        trade = "General Contractor"
        summary = f"The issue '{issue.title}' needs review and assignment to the correct responsible party."
        next_steps = [
            "Review the issue details",
            "Assign the responsible person or trade",
            "Set a follow-up deadline",
            "Track the issue until completion"
        ]
        tasks = [
            TaskRecommendation(
                title="Review and assign issue",
                assigned_to="Project Manager",
                priority="Medium"
            )
        ]

    return IssueAnalysis(
        category=category,
        urgency=urgency,
        trade=trade,
        summary=summary,
        next_steps=next_steps,
        tasks=tasks
    )


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "AI Consctruction Assistant API is running"
    }

@app.post("/issues", response_model=IssueResponse)
def create_issue(issue: IssueCreate, db: Session = Depends(get_db)):
    analysis = fake_ai_analyze_issue(issue)

    new_issue = Issue(
        title=issue.title,
        description=issue.description,
        project_namne=issue.project_name,
        location=issue.location,

        category=analysis.category,
        urgency=analysis.urgency,
        trade=analysis.trade,
        summary=analysis.summary,

        next_steps=json.dumps(analysis.next_steps),
        tasks=json.dumps([task.dict() for task in analysis.tasks])
    )

    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)

    return IssueResponse(
        id=new_issue.id,
        title=new_issue.title,
        description=new_issue.description,
        project_name=new_issue.project_name,
        location=new_issue.location,
        analysis=IssueAnalysis(
            category=new_issue.category,
            urgency=new_issue.urgency,
            trade=new_issue.trade,
            summary=new_issue.summary,
            next_steps=json.loads(new_issue.next_steps),
            tasks=[
                TaskRecommendation(**task)
                for task in json.loads(new_issue.tasks)
            ]
        )
    )
