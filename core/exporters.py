import json
from pathlib import Path
from typing import Union
from .schemas import MeetingAnalysis


def export_json(result: MeetingAnalysis) -> str:
    """Returns JSON string format of MeetingAnalysis."""
    return result.model_dump_json(indent=4)


def export_markdown(result: MeetingAnalysis) -> str:
    """
    Generates Executive Markdown Digest without symbols/emojis.
    Includes Action Items Table & Risk Matrix Table ready to copy/paste into Notion, Teams, or Slack.
    """
    md = []
    md.append("# Executive Meeting Digest")
    md.append("\n---\n")

    # 1. Summary
    md.append("## Executive Summary\n")
    md.append(result.summary)
    md.append("\n")

    # 2. Action Items Table
    md.append("## Action Items Matrix\n")
    if not result.action_items:
        md.append("No action items identified.\n")
    else:
        md.append("| # | Task Title | Assigned (Role) | Priority | Effort | Timeline | Acceptance Criteria |")
        md.append("|---|------------|-----------------|----------|--------|----------|---------------------|")

        for idx, item in enumerate(result.action_items, start=1):
            title = item.task_title.replace("|", "\\|")
            assigned = item.assigned.replace("|", "\\|")
            priority = item.priority
            effort = item.effort
            timeline = item.timeline
            criteria_str = "<br>".join([f"• {c.replace('|', '\\|')}" for c in item.acceptance_criteria])

            md.append(f"| {idx} | **{title}** | {assigned} | `{priority}` | `{effort}` | {timeline} | {criteria_str} |")
        md.append("\n")

    # 3. Decision Log
    md.append("## Architecture & Design Decisions\n")
    if not result.decisions:
        md.append("No decisions identified.\n")
    else:
        for idx, dec in enumerate(result.decisions, start=1):
            md.append(f"### Decision {idx}: {dec.decision}")
            md.append(f"**Rationale:** {dec.rationale}\n")

    # 4. Risk Matrix Table
    md.append("## Risk & Blocker Matrix\n")
    if not result.blockers:
        md.append("No blockers or risks identified.\n")
    else:
        md.append("| # | Risk / Blocker | Impact Assessment |")
        md.append("|---|----------------|-------------------|")

        for idx, block in enumerate(result.blockers, start=1):
            b_text = block.blocker.replace("|", "\\|")
            impact = block.impact.replace("|", "\\|")
            md.append(f"| {idx} | **{b_text}** | {impact} |")
        md.append("\n")

    return "\n".join(md)


def save_outputs(result: MeetingAnalysis, base_filename: Union[str, Path]):
    input_path = Path(base_filename)
    json_path = input_path.parent / f"{input_path.stem}_analysis.json"
    md_path = input_path.parent / f"{input_path.stem}_report.md"

    json_path.write_text(export_json(result), encoding="utf-8")
    md_path.write_text(export_markdown(result), encoding="utf-8")

    return json_path, md_path
