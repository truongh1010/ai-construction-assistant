from pydantic import BaseModel
from typing import List

class IssueCreate(BaseModel):
    title: str
    description: str
    project_name: str | None = None
    location: str | None = None

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
    Task: List[TaskRecommendation]