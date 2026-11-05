from pydantic import BaseModel
from typing import List, Literal, Optional


Urgency = Literal["Low", "Medium", "High", "Critical"]
IssueStatus = Literal["Open", "In Progress", "Resolved"]


class IssueCreate(BaseModel):
    title: str
    description: str
    project_name: Optional[str] = None
    location: Optional[str] = None


class TaskRecommendation(BaseModel):
    title: str
    assigned_to: str
    priority: Urgency


class IssueAnalysis(BaseModel):
    category: str
    urgency: Urgency
    trade: str
    summary: str
    next_steps: List[str]
    tasks: List[TaskRecommendation]


class IssueResponse(BaseModel):
    id: int
    title: str
    description: str
    project_name: Optional[str] = None
    location: Optional[str] = None
    status: IssueStatus
    analysis_source: str
    analysis: IssueAnalysis

    model_config = {
        "from_attributes": True
    }

class IssueStatusUpdate(BaseModel):
    status: IssueStatus


class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    project_name: Optional[str] = None
    location: Optional[str] = None