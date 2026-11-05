import json

from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import case
from sqlalchemy.orm import Session

from app.models import Issue
from app.schemas import IssueCreate, IssueResponse, IssueStatusUpdate, IssueUpdate
from app.database import Base, engine, SessionLocal

from app.ai_service import openai_analyze_issue, fake_ai_analyze_issue
from app.utils import build_issue_response

app = FastAPI(title="AI Construction Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "AI Construction Assistant API is running"
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
        print("OpenAI analysis failed. Falling back to the fake AI:", e)
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
        tasks=json.dumps([task.model_dump() for task in analysis.tasks]),
        analysis_source=analysis_source
    )

    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)

    return build_issue_response(new_issue)

@app.get("/issues", response_model=List[IssueResponse])
def get_issues(
    status: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "newest",
    db: Session = Depends(get_db)
):
    query = db.query(Issue)

    if status is not None and status != "All":
        query = query.filter(Issue.status == status)

    if search is not None and search.strip() != "":
        search_term = f"%{search.lower()}%"

        query = query.filter(
            Issue.status.ilike(search_term) |
            Issue.title.ilike(search_term) |
            Issue.description.ilike(search_term) |
            Issue.project_name.ilike(search_term) |
            Issue.location.ilike(search_term) |
            Issue.category.ilike(search_term) |
            Issue.urgency.ilike(search_term) |
            Issue.trade.ilike(search_term) |
            Issue.summary.ilike(search_term)
        )

    if sort_by == "oldest":
        query = query.order_by(Issue.id.asc())
    elif sort_by == "urgency":
        urgency_order = case(
            (Issue.urgency == "Critical", 4),
            (Issue.urgency == "High", 3),
            (Issue.urgency == "Medium", 2),
            (Issue.urgency == "Low", 1),
            else_=0
        )

        query = query.order_by(urgency_order.desc(), Issue.id.desc())
    elif sort_by == "status":
        query = query.order_by(
            Issue.status.asc(),
            Issue.id.desc()
        )
    else:
        query = query.order_by(Issue.id.desc())

    issues = query.all()

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
    issue.tasks = json.dumps([task.model_dump() for task in analysis.tasks])
    issue.analysis_source = analysis_source

    db.commit()
    db.refresh(issue)

    return build_issue_response(issue)