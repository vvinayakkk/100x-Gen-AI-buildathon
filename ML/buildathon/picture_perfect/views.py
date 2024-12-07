import os
import tempfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from transformers import pipeline

# Initialize the image captioning model
# This loads the model only once when the server starts
try:
    captioner = pipeline("image-to-text", model="Salesforce/blip-image-captioning-large")
except Exception as e:
    print(f"Error loading model: {e}")
    captioner = None

@csrf_exempt
def analyze_image(request):
    """
    Endpoint to receive an image file and generate an AI-powered response
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    # Check if model is loaded
    if captioner is None:
        return JsonResponse({'error': 'Image analysis model failed to load'}, status=500)
    
    try:
        # Check if image is in request files
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image file uploaded'}, status=400)
        
        # Get the uploaded image file
        image_file = request.FILES['image']
        
        # Validate file size (optional, adjust as needed)
        if image_file.size > 10 * 1024 * 1024:  # 10MB max
            return JsonResponse({'error': 'Image file too large'}, status=400)
        
        # Use tempfile to create a secure temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            # Write the uploaded file content
            for chunk in image_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        try:
            # Analyze the image
            captions = captioner(temp_file_path)
            
            # Generate a creative response based on the caption
            caption = captions[0]['generated_text']
            
            # Additional processing to make the response more engaging
            creative_response = generate_creative_response(caption)
            
            return JsonResponse({
                'original_caption': caption,
                'response': creative_response
            })
        
        finally:
            # Ensure temporary file is deleted
            try:
                os.unlink(temp_file_path)
            except Exception as delete_error:
                print(f"Warning: Could not delete temporary file {temp_file_path}: {delete_error}")
    
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

def generate_creative_response(caption):
    """
    Generate a more engaging response based on the image caption
    """
    # Simple response generation logic
    responses = [
        f"Wow, that's an interesting image! I see {caption}.",
        f"Let me put on my detective hat... looks like {caption}!",
        f"If this image could talk, it would say: '{caption}'",
        f"Just between us, this looks exactly like {caption}.",
        f"Breaking news: Confirmed sighting of {caption}!"
    ]
    
    # Randomly select a response
    import random
    return random.choice(responses)

def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'service': 'Picture Perfect Agent',
        'model_loaded': captioner is not None
    })