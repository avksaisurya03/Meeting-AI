import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core.preprocessor import preprocess_transcript
from core.analyzer import analyze_meeting
from core.exporters import export_json, export_markdown


def index(request):
    """Renders the main web interface."""
    return render(request, 'index.html')


@csrf_exempt
def analyze_api(request):
    """
    API view for processing meeting transcripts via file upload (.txt) or direct text.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    raw_text = ""
    filename = "meeting_transcript.txt"

    try:
        # 1. Handle File Upload
        if 'transcript_file' in request.FILES:
            uploaded_file = request.FILES['transcript_file']
            filename = uploaded_file.name
            raw_text = uploaded_file.read().decode('utf-8')

        # 2. Handle Raw Text Input
        elif request.content_type == 'application/json':
            body = json.loads(request.body.decode('utf-8'))
            raw_text = body.get('transcript_text', '')
        else:
            raw_text = request.POST.get('transcript_text', '')

        if not raw_text or not raw_text.strip():
            return JsonResponse({'error': 'No transcript content provided. Please upload a .txt file or paste meeting text.'}, status=400)

        # 3. Preprocess Transcript
        cleaned_text = preprocess_transcript(raw_text)

        # 4. Analyze Meeting via Azure OpenAI
        result = analyze_meeting(cleaned_text)

        # 5. Export JSON and Markdown (with Action Items Table)
        json_output = json.loads(export_json(result))
        markdown_output = export_markdown(result)

        return JsonResponse({
            'success': True,
            'filename': filename,
            'data': json_output,
            'markdown': markdown_output
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
