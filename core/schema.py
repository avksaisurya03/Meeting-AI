from pydantic import BaseModel, Field

class ActionItem(BaseModel):
    task_title: str = Field(
        description="Specific action item including the relevant project, system, feature, or component"
    )
    assigned: str = Field(
        description="Person assigned to the task. Include their role in parentheses when it can be reliably determined."
    )
    priority: str = Field(
        description="Priority: High, Medium, or Low"
    )
    effort: str = Field(
        description="Effort: Simple, Moderate, or Complex"
    )
    timeline: str = Field(
        description="Deadline or timeframe mentioned in the meeting"
    )
    acceptance_criteria: list[str] = Field(
        description="Conditions that indicate the task is completed"
    )

class Decision(BaseModel):
    decision: str = Field(
        description="Decision explicitly made or agreed upon"
    )
    rationale: str = Field(
        description="Reason for making the decision based on the meeting"
    )

class Blocker(BaseModel):
    blocker: str = Field(
        description="Specific blocker identified in the meeting"
    )
    impact: str = Field(
        description="Impact of the blocker based only on the meeting"
    )

class MeetingAnalysis(BaseModel):
    summary: str
    action_items: list[ActionItem]
    decisions: list[Decision]
    blockers: list[Blocker]
