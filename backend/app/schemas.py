from pydantic import BaseModel
from typing import List, Optional


class IssueCreate(BaseModel):
    title: str
    description: str
    project_name: Optional[str] = None
    location: Optional[str] = None


class TaskRecommendation(BaseModel):
    title: str
    assigned_to: str
    priority: str


class IssueAnalysis(BaseModel):
    category: str
    urgency: str
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
    analysis_source: str
    analysis: IssueAnalysis

    model_config = {
        "from_attributes": True
    }