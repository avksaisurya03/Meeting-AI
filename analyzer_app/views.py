import json
from django.shortcuts import render, redirect
from core.preprocessing import preprocess_transcript
from core.azure import analyze_meeting
from core.report import export_json, export_markdown
from core.database import save_meeting_analysis, get_all_meetings, get_meeting_analysis_by_id
from core.schema import MeetingAnalysis, ActionItem, Decision, Blocker

def home_view(request):
    """Renders the main upload & paste web interface with recent meeting history."""
    past_meetings = get_all_meetings()
    return render(request, 'meeting/home.html', {
        'active_tab': 'file',
        'past_meetings': past_meetings
    })

def analyze_view(request):
    """Processes the transcript and saves it to Supabase or falls back to direct render."""
    if request.method != 'POST':
        return redirect('home')

    raw_text = ""
    filename = "Pasted Text"
    active_tab = 'file'
    past_meetings = get_all_meetings()

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

        # Build exports for formatting
        json_output = export_json(result)
        markdown_output = export_markdown(result)

        try:
            # 1. Attempt to Save to Supabase (Transactional insert)
            meeting_id = save_meeting_analysis(
                filename=filename,
                raw_text=cleaned_text,
                summary=result.summary,
                action_items=result.action_items,
                decisions=result.decisions,
                blockers=result.blockers
            )
            # Redirect to the detail view URL for persistent page loads
            return redirect('meeting_detail', meeting_id=meeting_id)

        except ValueError as db_err:
            # Supabase environment variables are missing (Local-only mode)
            # Fallback to direct rendering
            context = {
                'filename': filename,
                'summary': result.summary,
                'action_items': result.action_items,
                'decisions': result.decisions,
                'blockers': result.blockers,
                'markdown_content': markdown_output,
                'json_content': json_output,
                'db_warning': str(db_err)  # Alert user they are in local mode
            }
            return render(request, 'meeting/result.html', context)

    except Exception as e:
        return render(request, 'meeting/home.html', {
            'error': f'Analysis failed: {str(e)}',
            'active_tab': active_tab,
            'transcript_text': request.POST.get('transcript_text', ''),
            'past_meetings': past_meetings
        })

def meeting_detail_view(request, meeting_id):
    """Retrieves a saved meeting analysis from Supabase and renders it."""
    try:
        data = get_meeting_analysis_by_id(str(meeting_id))
        
        # Reconstruct the Pydantic object to leverage standard exporters
        analysis_obj = MeetingAnalysis(
            summary=data['summary'],
            action_items=[
                ActionItem(
                    task_title=item.get('task_title'),
                    assigned=item.get('assigned'),
                    priority=item.get('priority'),
                    effort=item.get('effort'),
                    timeline=item.get('timeline'),
                    acceptance_criteria=item.get('acceptance_criteria', [])
                ) for item in data['action_items']
            ],
            decisions=[
                Decision(
                    decision=dec.get('decision'),
                    rationale=dec.get('rationale')
                ) for dec in data['decisions']
            ],
            blockers=[
                Blocker(
                    blocker=b.get('blocker'),
                    impact=b.get('impact')
                ) for b in data['blockers']
            ]
        )
        
        markdown_output = export_markdown(analysis_obj)
        json_output = export_json(analysis_obj)

        context = {
            'filename': data['filename'],
            'summary': data['summary'],
            'action_items': data['action_items'],
            'decisions': data['decisions'],
            'blockers': data['blockers'],
            'markdown_content': markdown_output,
            'json_content': json_output
        }
        return render(request, 'meeting/result.html', context)
        
    except Exception as e:
        past_meetings = get_all_meetings()
        return render(request, 'meeting/home.html', {
            'error': f'Failed to load saved meeting: {str(e)}',
            'active_tab': 'file',
            'past_meetings': past_meetings
        })
