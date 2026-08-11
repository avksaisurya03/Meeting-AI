import json
from django.shortcuts import render, redirect
from core.preprocessing import preprocess_transcript
from core.azure import analyze_meeting
from core.report import export_json, export_markdown

def home_view(request):
    """Renders the main upload & paste web interface."""
    return render(request, 'meeting/home.html', {'active_tab': 'file'})

def analyze_view(request):
    """Processes the transcript and renders the result page or redirects on error."""
    if request.method != 'POST':
        return redirect('home')

    raw_text = ""
    filename = "Pasted Text"
    active_tab = 'file'

    try:
        # Determine source: File Upload or Raw Text
        source_type = request.POST.get('source_type', 'file')

        if source_type == 'file':
            active_tab = 'file'
            if 'transcript_file' not in request.FILES:
                return render(request, 'meeting/home.html', {
                    'error': 'Please select a .txt transcript file to upload.',
                    'active_tab': active_tab
                })
            
            uploaded_file = request.FILES['transcript_file']
            filename = uploaded_file.name

            # Server-side validation: extension check
            if not filename.lower().endswith('.txt'):
                return render(request, 'meeting/home.html', {
                    'error': 'Invalid file format. Only .txt transcript files are supported.',
                    'active_tab': active_tab
                })

            # Server-side validation: file size limit (2 MB)
            if uploaded_file.size > 2 * 1024 * 1024:
                return render(request, 'meeting/home.html', {
                    'error': 'File size exceeds the 2 MB limit.',
                    'active_tab': active_tab
                })

            try:
                raw_text = uploaded_file.read().decode('utf-8')
            except Exception:
                return render(request, 'meeting/home.html', {
                    'error': 'Failed to read the file. Please ensure it is a valid text file.',
                    'active_tab': active_tab
                })

            if not raw_text.strip():
                return render(request, 'meeting/home.html', {
                    'error': 'The uploaded transcript file is empty.',
                    'active_tab': active_tab
                })

        else:  # source_type == 'text'
            active_tab = 'text'
            raw_text = request.POST.get('transcript_text', '').strip()

            if not raw_text:
                return render(request, 'meeting/home.html', {
                    'error': 'Please paste your meeting transcript before submitting.',
                    'active_tab': active_tab
                })

            # Server-side validation: word count limit (1500 words)
            word_count = len(raw_text.split())
            if word_count > 1500:
                return render(request, 'meeting/home.html', {
                    'error': f'Pasted text exceeds the 1500 words limit (Current: {word_count} words).',
                    'active_tab': active_tab,
                    'transcript_text': raw_text
                })

        # Process and analyze
        cleaned_text = preprocess_transcript(raw_text)
        result = analyze_meeting(cleaned_text)

        # Build exports for frontend copy operations
        json_output = export_json(result)
        markdown_output = export_markdown(result)

        context = {
            'filename': filename,
            'summary': result.summary,
            'action_items': result.action_items,
            'decisions': result.decisions,
            'blockers': result.blockers,
            'markdown_content': markdown_output,
            'json_content': json_output
        }

        return render(request, 'meeting/result.html', context)

    except Exception as e:
        return render(request, 'meeting/home.html', {
            'error': f'Analysis failed: {str(e)}',
            'active_tab': active_tab,
            'transcript_text': request.POST.get('transcript_text', '')
        })
