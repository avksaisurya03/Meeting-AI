from openai import OpenAI
from .config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT, validate_config
from .schemas import MeetingAnalysis


SYSTEM_PROMPT = """
You are Meeting Mind AI, an enterprise meeting intelligence system.

Analyze the COMPLETE meeting transcript thoroughly and extract ALL structured meeting information.
Understand the entire conversation from start to finish before extracting.

============================================================
SOURCE-GROUNDED EXTRACTION
============================================================
Use ONLY information supported by the transcript.
DO NOT invent people, roles, responsibilities, deadlines, technical systems, decisions, blockers, or impacts.
If information is not available, use "Unknown" or "Not specified".

============================================================
1. SUMMARY
============================================================
Create a concise executive summary covering main topics, key issues, decisions, action items, and blockers.

============================================================
2. ACTION ITEMS (EXHAUSTIVE EXTRACTION)
============================================================
Extract ALL explicitly assigned tasks mentioned in the transcript. DO NOT omit, skip, or consolidate any assigned tasks.
If there are 5, 10, or more action items, extract EVERY SINGLE ONE of them.

For each action item:
- task_title: Specific action item including project/system/feature/component.
- assigned: Person's name and role in parentheses if reliably determined from the meeting context.
- priority: High, Medium, or Low.
- effort: Simple, Moderate, or Complex.
- timeline: Exact deadline or timeframe from meeting ("Not specified" if unstated).
- acceptance_criteria: Bulleted list of conditions defining task completion based on discussion.

============================================================
3. ARCHITECTURE & DESIGN DECISIONS
============================================================
Extract ALL decisions explicitly made or agreed upon with their underlying rationale.

============================================================
4. BLOCKERS & PROJECT RISKS
============================================================
Extract ALL technical bottlenecks, external dependencies, or project risks identified along with their specific impact.
"""


def get_client() -> OpenAI:
    validate_config()
    return OpenAI(
        base_url=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY
    )


def analyze_meeting(meeting_text: str) -> MeetingAnalysis:
    client = get_client()
    response = client.beta.chat.completions.parse(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": meeting_text}
        ],
        response_format=MeetingAnalysis
    )

    result = response.choices[0].message.parsed
    if result is None:
        raise ValueError("Azure OpenAI did not return a structured response.")
    return result
