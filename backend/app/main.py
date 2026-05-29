import os
import json

from typing import List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routes import issues

from sqlalchemy.orm import Session, session
from app.models import Issue
from app.schemas import IssueAnalysis, IssueCreate, IssueResponse, TaskRecommendation, IssueStatusUpdate, IssueUpdate
from app.database import Base, engine, SessionLocal

from app.ai_service import openai_analyze_issue, fake_ai_analyze_issue
from app.utils import build_issue_response

from typing import List, Optional

app = FastAPI(title="AI Construction Assistant API")

# load_dotenv()

# api_key = os.getenv("OPENAI_API_KEY")

# client = OpenAI(api_key=api_key)

# def openai_analyze_issue(issue: IssueCreate) -> IssueAnalysis:

#     system_prompt = f"""
#     You are an AI assistant for construction project issue tracking.

#     Analyze a provided construction issue and return ONLY valid JSON. No Markdown. No Explanation.

#     Return JSON with exactly this structure:
#     {{
#         "category": "string",
#         "urgency": "Low | Medium | High | Critical",
#         "trade": "string",
#         "summary": "string",
#         "next_steps": ["string", "string", "string"],
#         "tasks": [
#             {{
#                 "title": "string",
#                 "assigned_to": "string",
#                 "priority": "Low | Medium | High | Critical"
#             }}
#         ]
#     }}
#     """

#     user_prompt = f"""
#     Analyze the following construction issue:

#     Issue title: {issue.title}
#     Description: {issue.description}
#     Project name: {issue.project_name}
#     Location: {issue.location}
#     """

#     response = client.chat.completions.create(
#         model="gpt-4.1-mini",
#         messages=[
#             {
#                 "role": "system",
#                 "content": system_prompt
#             },
#             {
#                 "role": "user",
#                 "content": user_prompt
#             }
#         ],
#         temperature=0.2
#     )

#     content = response.choices[0].message.content
#     data = json.loads(content)

#     return IssueAnalysis(
#         category=data["category"],
#         urgency=data["urgency"],
#         trade=data["trade"],
#         summary=data["summary"],
#         next_steps=data["next_steps"],
#         tasks=[
#             TaskRecommendation(**task)
#             for task in data["tasks"]
#         ]
#     )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
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

# def fake_ai_analyze_issue(issue: IssueCreate) -> IssueAnalysis:
#     description = issue.description.lower()

#     if "delay" in description or "late" in description or "schedule" in description:
#         category = "Schedule"
#         urgency = "High"
#         trade = "Project Management"
#         summary = f"The issue '{issue.title}' appears to affect the project schedule."
#         next_steps = [
#             "Review the current project schedule",
#             "Identify the delayed activity or dependency",
#             "Contact the responsible subcontractor or supplier",
#             "Update stakeholders about the possible schedule impact"
#         ]
#         tasks = [
#             TaskRecommendation(
#                 title="Review project schedule impact",
#                 assigned_to="Project Manager",
#                 priority="High"
#             ),
#             TaskRecommendation(
#                 title="Follow up with responsible party",
#                 assigned_to="Site Supervisor",
#                 priority="High"
#             )
#         ]

#     elif "cost" in description or "budget" in description or "expensive" in description:
#         category = "Budget"
#         urgency = "Medium"
#         trade = "Project Management"
#         summary = f"The issue '{issue.title}' appears to involve a budget or cost concern."
#         next_steps = [
#             "Review the original budget",
#             "Estimate the cost impact",
#             "Document the reason for the cost change",
#             "Prepare a change order if needed"
#         ]
#         tasks = [
#             TaskRecommendation(
#                 title="Estimate cost impact",
#                 assigned_to="Project Manager",
#                 priority="Medium"
#             ),
#             TaskRecommendation(
#                 title="Prepare change order draft",
#                 assigned_to="Project Coordinator",
#                 priority="Medium"
#             )
#         ]

#     elif "safety" in description or "hazard" in description or "injury" in description:
#         category = "Safety"
#         urgency = "Critical"
#         trade = "Site Safety"
#         summary = f"The issue '{issue.title}' appears to involve a safety risk that needs immediate attention."
#         next_steps = [
#             "Secure the affected area",
#             "Stop related work if necessary",
#             "Notify the site supervisor immediately",
#             "Document the safety concern and assign corrective action"
#         ]
#         tasks = [
#             TaskRecommendation(
#                 title="Secure affected area",
#                 assigned_to="Site Supervisor",
#                 priority="Critical"
#             ),
#             TaskRecommendation(
#                 title="Document safety issue",
#                 assigned_to="Safety Officer",
#                 priority="Critical"
#             )
#         ]

#     elif "leak" in description or "water" in description or "pipe" in description:
#         category = "Plumbing"
#         urgency = "High"
#         trade = "Plumber"
#         summary = f"The issue '{issue.title}' appears to involve a plumbing problem that may require quick inspection."
#         next_steps = [
#             "Inspect the affected area",
#             "Identify the source of the leak or water issue",
#             "Contact the plumbing subcontractor",
#             "Document photos and update the issue log"
#         ]
#         tasks = [
#             TaskRecommendation(
#                 title="Inspect water issue on site",
#                 assigned_to="Site Supervisor",
#                 priority="High"
#             ),
#             TaskRecommendation(
#                 title="Contact plumbing subcontractor",
#                 assigned_to="Project Manager",
#                 priority="High"
#             )
#         ]

#     elif "electrical" in description or "power" in description or "wire" in description:
#         category = "Electrical"
#         urgency = "High"
#         trade = "Electrician"
#         summary = f"The issue '{issue.title}' appears to involve electrical work and should be reviewed for safety."
#         next_steps = [
#             "Stop work in the affected area if unsafe",
#             "Inspect the electrical issue",
#             "Notify the electrical subcontractor",
#             "Verify work meets safety requirements"
#         ]
#         tasks = [
#             TaskRecommendation(
#                 title="Inspect electrical issue",
#                 assigned_to="Electrician",
#                 priority="High"
#             ),
#             TaskRecommendation(
#                 title="Verify site safety",
#                 assigned_to="Site Supervisor",
#                 priority="High"
#             )
#         ]

#     else:
#         category = "General"
#         urgency = "Medium"
#         trade = "General Contractor"
#         summary = f"The issue '{issue.title}' needs review and assignment to the correct responsible party."
#         next_steps = [
#             "Review the issue details",
#             "Assign the responsible person or trade",
#             "Set a follow-up deadline",
#             "Track the issue until completion"
#         ]
#         tasks = [
#             TaskRecommendation(
#                 title="Review and assign issue",
#                 assigned_to="Project Manager",
#                 priority="Medium"
#             )
#         ]

#     return IssueAnalysis(
#         category=category,
#         urgency=urgency,
#         trade=trade,
#         summary=summary,
#         next_steps=next_steps,
#         tasks=tasks
#     )

# def build_issue_response(issue: Issue) -> IssueResponse:
#     return IssueResponse(
#         id=issue.id,
#         title=issue.title,
#         description=issue.description,
#         project_name=issue.project_name,
#         location=issue.location,
#         status=issue.status,
#         analysis=IssueAnalysis(
#             category=issue.category,
#             urgency=issue.urgency,
#             trade=issue.trade,
#             summary=issue.summary,
#             next_steps=json.loads(issue.next_steps),
#             tasks=[
#                 TaskRecommendation(**task)
#                 for task in json.loads(issue.tasks)
#             ]
#         ),
#         analysis_source=issue.analysis_source
#     )

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "AI Consctruction Assistant API is running"
    }

@app.post("/issues", response_model=IssueResponse)
def create_issue(
    issue: IssueCreate, 
    db: Session = Depends(get_db)
):
    try:
        analysis = openai_analyze_issue(issue)
        analysis_source = "openai"
    except Exception as e:
        print("OpenAI analysis failed. Falling back to the fake AI:")
        analysis = fake_ai_analyze_issue(issue)
        analysis_source = "fallback"

    new_issue = Issue(
        title=issue.title,
        description=issue.description,
        project_name=issue.project_name,
        location=issue.location,
        status="Open",

        category=analysis.category,
        urgency=analysis.urgency,
        trade=analysis.trade,
        summary=analysis.summary,

        next_steps=json.dumps(analysis.next_steps),
        tasks=json.dumps([task.dict() for task in analysis.tasks]),
        analysis_source=analysis_source
    )

    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)

    return build_issue_response(new_issue)

# @app.get("/issues", response_model=List[IssueResponse])
# def get_issues(db: Session = Depends(get_db)):
#     issues = db.query(Issue).order_by(Issue.id.desc()).all()

#     return [
#         build_issue_response(issue)
#             for issue in issues
#     ]

@app.get("/issues", response_model=List[IssueResponse])
def get_issues(
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Issue)

    if status is not None and status != "All":
        query = query.filter(Issue.status == status)

    if search is not None and search.strip() != "":
        search_term = f"%{search.lower()}%"

        query = query.filter(
            Issue.title.ilike(search_term) |
            Issue.description.ilike(search_term) |
            Issue.project_name.ilike(search_term) |
            Issue.location.ilike(search_term) |
            Issue.category.ilike(search_term) |
            Issue.urgency.ilike(search_term) |
            Issue.trade.ilike(search_term) |
            Issue.summary.ilike(search_term)
        )

    issues = query.order_by(Issue.id.desc()).all()

    return [build_issue_response(issue) for issue in issues]

# get issue by id
@app.get("/issues/{issue_id}", response_model=IssueResponse)
def get_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    return build_issue_response(issue)

# delete issue by id
@app.delete("/issues/{issue_id}")
def delete_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    db.delete(issue)
    db.commit()

    return {"message": f"Issue {issue_id} deleted successfully"}

@app.patch("/issues/{issue_id}/status")
def update_issue_status(
    issue_id: int,
    status_update: IssueStatusUpdate,
    db: Session = Depends(get_db)
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found.")

    allowed_statuses = ["Open", "In progress", "Resolved"]

    if status_update.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid status. Open, In progress, or Resolved"
        )

    issue.status = status_update.status

    db.commit()
    db.refresh(issue)

    return build_issue_response(issue)

@app.put("/issues/{issue_id}", response_model=IssueResponse)
def update_issue(
    issue_id: int,
    issue_update: IssueUpdate,
    db: Session = Depends(get_db)
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    if issue_update.title is not None:
        issue.title = issue_update.title

    if issue_update.description is not None:
        issue.description = issue_update.description

    if issue_update.project_name is not None:
        issue.project_name = issue_update.project_name

    if issue_update.location is not None:
        issue.location = issue_update.location

    db.commit()
    db.refresh(issue)

    return build_issue_response(issue)

@app.post("/issues/{issue_id}/reanalyze", response_model=IssueResponse)
def reanalyze_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    issue_input = IssueCreate(
        title=issue.title,
        description=issue.description,
        project_name=issue.project_name,
        location=issue.location,
    )

    try:
        analysis = openai_analyze_issue(issue_input)
        analysis_source = "openai"
    except Exception as e:
        print("OpenAI reanalysis failed. Falling back to fake AI:", e)
        analysis = fake_ai_analyze_issue(issue_input)
        analysis_source = "fallback"

    issue.category = analysis.category
    issue.urgency = analysis.urgency
    issue.trade = analysis.trade
    issue.summary = analysis.summary
    issue.next_steps = json.dumps(analysis.next_steps)
    issue.tasks = json.dumps([task.dict() for task in analysis.tasks])
    issue.analysis_source = analysis_source

    db.commit()
    db.refresh(issue)

    return build_issue_response(issue)