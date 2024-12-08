from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import asyncio
from .tweet_analyzer import TweetAnalyzer
import tempfile
import os

analyzer = TweetAnalyzer()

@csrf_exempt
@require_http_methods(["POST"])
def analyze_tweet(request):
    try:
        # Check if analysis type is specified
        analysis_type = request.POST.get('analysis_type', 'default')
        
        # Check if image file is in the request
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image file provided'}, status=400)
        
        image_file = request.FILES['image']
        
        # Validate file type (optional)
        allowed_types = ['image/jpeg', 'image/png']
        if image_file.content_type not in allowed_types:
            return JsonResponse({
                'error': 'Invalid file type. Only JPEG and PNG files are allowed'
            }, status=400)
        
        # Create a temporary file to store the image
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image_file.name)[1]) as temp_file:
            for chunk in image_file.chunks():
                temp_file.write(chunk)
            temp_path = temp_file.name

        try:
            # Run the analysis
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            report = loop.run_until_complete(analyzer.generate_report(temp_path))
            formatted_report = analyzer.format_report(report)

            # Additional processing based on analysis type could be added here
            additional_processing = {}
            if analysis_type == 'detailed':
                # Add more detailed analysis or specific processing
                additional_processing['extra_details'] = 'Detailed analysis requested'
            elif analysis_type == 'summary':
                # Potentially generate a more concise report
                additional_processing['summary'] = 'Condensed analysis'

            return JsonResponse({
                'success': True,
                'report': formatted_report,
                'extracted_text': report.get('extracted_text', ''),
                'analysis': report.get('analysis', {}),
                'analysis_type': analysis_type,
                'additional_processing': additional_processing
            })

        finally:
            # Clean up the temporary file
            os.unlink(temp_path)
            loop.close()

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)