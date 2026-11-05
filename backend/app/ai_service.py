import os
from functools import lru_cache

from dotenv import load_dotenv
from openai import OpenAI

from app.schemas import IssueCreate, IssueAnalysis, TaskRecommendation

load_dotenv()

# created on first use: OpenAI() raises when the key is missing, and that has
# to happen inside the try/except in the routes so the fallback can take over
@lru_cache(maxsize=1)
def get_client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

def openai_analyze_issue(issue: IssueCreate) -> IssueAnalysis:

    system_prompt = """
    You are an AI assistant for construction project issue tracking.

    Analyze a provided construction issue. Give at least three next steps.
    """

    user_prompt = f"""
    Analyze the following construction issue:

    Issue title: {issue.title}
    Description: {issue.description}
    Project name: {issue.project_name}
    Location: {issue.location}
    """

    response = get_client().chat.completions.parse(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0.2,
        response_format=IssueAnalysis
    )

    message = response.choices[0].message

    # a refusal comes back as a normal response with nothing parsed
    if message.parsed is None:
        raise ValueError(f"OpenAI returned no analysis: {message.refusal}")

    return message.parsed


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
