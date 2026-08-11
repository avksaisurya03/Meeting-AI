import os
from supabase import create_client, Client
from .schema import MeetingAnalysis

def get_supabase_client() -> Client:
    """Initializes and returns the Supabase client."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    # Check if placeholders are still present
    if not url or not key or "your-project-id" in url or "your-supabase-service-role" in key:
        raise ValueError(
            "Supabase connection is not configured. Please edit your '.env' file "
            "and replace the placeholder SUPABASE_URL and SUPABASE_KEY with your actual credentials."
        )
    return create_client(url, key)

def save_meeting_analysis(filename: str, raw_text: str, summary: str, action_items: list, decisions: list, blockers: list) -> str:
    """
    Saves a completed meeting analysis and all related cards to Supabase.
    Returns the generated meeting_id UUID.
    """
    client = get_supabase_client()

    # 1. Insert master meeting row
    meeting_payload = {
        "filename": filename,
        "raw_text": raw_text,
        "summary": summary
    }
    meeting_res = client.table("meetings").insert(meeting_payload).execute()
    
    if not meeting_res.data or len(meeting_res.data) == 0:
        raise Exception("Database failed to insert master meeting log.")
    
    meeting_id = meeting_res.data[0]["id"]

    # 2. Bulk Insert Action Items
    if action_items:
        action_payloads = []
        for item in action_items:
            # Handle Pydantic model serialization or standard dict
            item_data = item.model_dump() if hasattr(item, "model_dump") else dict(item)
            action_payloads.append({
                "meeting_id": meeting_id,
                "task_title": item_data.get("task_title"),
                "assigned": item_data.get("assigned"),
                "priority": item_data.get("priority"),
                "effort": item_data.get("effort"),
                "timeline": item_data.get("timeline"),
                "acceptance_criteria": item_data.get("acceptance_criteria", [])
            })
        client.table("action_items").insert(action_payloads).execute()

    # 3. Bulk Insert Decisions
    if decisions:
        decision_payloads = []
        for dec in decisions:
            dec_data = dec.model_dump() if hasattr(dec, "model_dump") else dict(dec)
            decision_payloads.append({
                "meeting_id": meeting_id,
                "decision": dec_data.get("decision"),
                "rationale": dec_data.get("rationale")
            })
        client.table("decisions").insert(decision_payloads).execute()

    # 4. Bulk Insert Project Risks
    if blockers:
        risk_payloads = []
        for b in blockers:
            b_data = b.model_dump() if hasattr(b, "model_dump") else dict(b)
            risk_payloads.append({
                "meeting_id": meeting_id,
                "blocker": b_data.get("blocker"),
                "impact": b_data.get("impact")
            })
        client.table("project_risks").insert(risk_payloads).execute()

    return meeting_id

def get_all_meetings() -> list:
    """Returns a list of all processed meeting master headers (id, filename, created_at)."""
    try:
        client = get_supabase_client()
        res = client.table("meetings").select("id, filename, created_at").order("created_at", desc=True).execute()
        return res.data or []
    except Exception:
        # Fallback to empty list if Supabase is not configured yet
        return []

def get_meeting_analysis_by_id(meeting_id: str) -> dict:
    """
    Fetches a saved meeting analysis from Supabase and formats it for presentation.
    """
    client = get_supabase_client()

    # Fetch meeting header details
    meeting_res = client.table("meetings").select("*").eq("id", meeting_id).execute()
    if not meeting_res.data:
        raise Exception(f"No meeting found with ID {meeting_id}")
    
    meeting = meeting_res.data[0]

    # Fetch child tables
    actions_res = client.table("action_items").select("*").eq("meeting_id", meeting_id).execute()
    decisions_res = client.table("decisions").select("*").eq("meeting_id", meeting_id).execute()
    risks_res = client.table("project_risks").select("*").eq("meeting_id", meeting_id).execute()

    # Format data structurally matching result context
    return {
        "filename": meeting["filename"],
        "summary": meeting["summary"],
        "action_items": actions_res.data or [],
        "decisions": decisions_res.data or [],
        "blockers": risks_res.data or []
    }
