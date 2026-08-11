import json
from django.shortcuts import render, redirect
from core.preprocessing import preprocess_transcript
from core.azure import analyze_meeting
from core.report import export_json, export_markdown
from core.schema import MeetingAnalysis, ActionItem as SchemaActionItem, Decision as SchemaDecision, Blocker as SchemaBlocker
from .models import Meeting, ActionItem, Decision, ProjectRisk

def home_view(request):
    """Renders the main upload & paste web interface with recent meeting history."""
    past_meetings = Meeting.objects.all().order_by('-created_at')
    return render(request, 'meeting/home.html', {
        'active_tab': 'file',
        'past_meetings': past_meetings
    })

def analyze_view(request):
    """Processes the transcript and saves it directly to the local SQLite database."""
    if request.method != 'POST':
        return redirect('home')

    raw_text = ""
    filename = "Pasted Text"
    active_tab = 'file'
    past_meetings = Meeting.objects.all().order_by('-created_at')

    try:
        # Determine source: File Upload or Raw Text
        source_type = request.POST.get('source_type', 'file')

        if source_type == 'file':
            active_tab = 'file'
            if 'transcript_file' not in request.FILES:
                return render(request, 'meeting/home.html', {
                    'error': 'Please select a .txt transcript file to upload.',
                    'active_tab': active_tab,
                    'past_meetings': past_meetings
                })
            
            uploaded_file = request.FILES['transcript_file']
            filename = uploaded_file.name

            # Server-side validation: extension check
            if not filename.lower().endswith('.txt'):
                return render(request, 'meeting/home.html', {
                    'error': 'Invalid file format. Only .txt transcript files are supported.',
                    'active_tab': active_tab,
                    'past_meetings': past_meetings
                })

            # Server-side validation: file size limit (2 MB)
            if uploaded_file.size > 2 * 1024 * 1024:
                return render(request, 'meeting/home.html', {
                    'error': 'File size exceeds the 2 MB limit.',
                    'active_tab': active_tab,
                    'past_meetings': past_meetings
                })

            try:
                raw_text = uploaded_file.read().decode('utf-8')
            except Exception:
                return render(request, 'meeting/home.html', {
                    'error': 'Failed to read the file. Please ensure it is a valid text file.',
                    'active_tab': active_tab,
                    'past_meetings': past_meetings
                })

            if not raw_text.strip():
                return render(request, 'meeting/home.html', {
                    'error': 'The uploaded transcript file is empty.',
                    'active_tab': active_tab,
                    'past_meetings': past_meetings
                })

        else:  # source_type == 'text'
            active_tab = 'text'
            raw_text = request.POST.get('transcript_text', '').strip()

            if not raw_text:
                return render(request, 'meeting/home.html', {
                    'error': 'Please paste your meeting transcript before submitting.',
                    'active_tab': active_tab,
                    'past_meetings': past_meetings
                })

            # Server-side validation: word count limit (1500 words)
            word_count = len(raw_text.split())
            if word_count > 1500:
                return render(request, 'meeting/home.html', {
                    'error': f'Pasted text exceeds the 1500 words limit (Current: {word_count} words).',
                    'active_tab': active_tab,
                    'transcript_text': raw_text,
                    'past_meetings': past_meetings
                })

        # Process and analyze via Azure OpenAI
        cleaned_text = preprocess_transcript(raw_text)
        result = analyze_meeting(cleaned_text)

        # 1. Create master meeting row
        meeting = Meeting.objects.create(
            filename=filename,
            raw_text=cleaned_text,
            summary=result.summary
        )

        # 2. Bulk Insert Action Items
        if result.action_items:
            action_items_to_create = []
            for item in result.action_items:
                action_items_to_create.append(ActionItem(
                    meeting=meeting,
                    task_title=item.task_title,
                    assigned=item.assigned,
                    priority=item.priority,
                    effort=item.effort,
                    timeline=item.timeline,
                    acceptance_criteria=item.acceptance_criteria
                ))
            ActionItem.objects.bulk_create(action_items_to_create)

        # 3. Bulk Insert Decisions
        if result.decisions:
            decisions_to_create = []
            for dec in result.decisions:
                decisions_to_create.append(Decision(
                    meeting=meeting,
                    decision=dec.decision,
                    rationale=dec.rationale
                ))
            Decision.objects.bulk_create(decisions_to_create)

        # 4. Bulk Insert Project Risks
        if result.blockers:
            risks_to_create = []
            for b in result.blockers:
                risks_to_create.append(ProjectRisk(
                    meeting=meeting,
                    blocker=b.blocker,
                    impact=b.impact
                ))
            ProjectRisk.objects.bulk_create(risks_to_create)

        # Redirect to the detail view URL for persistent page loads
        return redirect('meeting_detail', meeting_id=meeting.id)

    except Exception as e:
        return render(request, 'meeting/home.html', {
            'error': f'Analysis failed: {str(e)}',
            'active_tab': active_tab,
            'transcript_text': request.POST.get('transcript_text', ''),
            'past_meetings': past_meetings
        })

def meeting_detail_view(request, meeting_id):
    """Retrieves a saved meeting analysis from local SQLite and renders it."""
    try:
        meeting = Meeting.objects.get(id=meeting_id)
        
        # Query child relationships
        action_items = meeting.action_items.all()
        decisions = meeting.decisions.all()
        blockers = meeting.project_risks.all()

        # Reconstruct the Pydantic object to leverage standard exporters
        analysis_obj = MeetingAnalysis(
            summary=meeting.summary,
            action_items=[
                SchemaActionItem(
                    task_title=item.task_title,
                    assigned=item.assigned,
                    priority=item.priority,
                    effort=item.effort,
                    timeline=item.timeline,
                    acceptance_criteria=item.acceptance_criteria
                ) for item in action_items
            ],
            decisions=[
                SchemaDecision(
                    decision=dec.decision,
                    rationale=dec.rationale
                ) for dec in decisions
            ],
            blockers=[
                SchemaBlocker(
                    blocker=b.blocker,
                    impact=b.impact
                ) for b in blockers
            ]
        )
        
        markdown_output = export_markdown(analysis_obj)
        json_output = export_json(analysis_obj)

        context = {
            'filename': meeting.filename,
            'summary': meeting.summary,
            'action_items': action_items,
            'decisions': decisions,
            'blockers': blockers,
            'markdown_content': markdown_output,
            'json_content': json_output
        }
        return render(request, 'meeting/result.html', context)
        
    except Meeting.DoesNotExist:
        past_meetings = Meeting.objects.all().order_by('-created_at')
        return render(request, 'meeting/home.html', {
            'error': 'The requested meeting analysis could not be found.',
            'active_tab': 'file',
            'past_meetings': past_meetings
        })
