import os
import tempfile
import random
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# Transformers and Image Captioning
from transformers import pipeline

# Langchain Imports
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

class PicturePerfectAgent:
    def __init__(self):
        """
        Initialize image captioning and response generation components
        """
        # Initialize image captioning model
        try:
            self.captioner = pipeline("image-to-text", model="Salesforce/blip-image-captioning-large")
        except Exception as e:
            print(f"Error loading image captioning model: {e}")
            self.captioner = None
        
        # Initialize Gemini model for creative responses
        try:
            self.gemini_model = ChatGoogleGenerativeAI(
                model="gemini-pro",
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0.1
            )
        except Exception as e:
            print(f"Error loading Gemini model: {e}")
            self.gemini_model = None
        
        # Detailed prompt template for generating responses
        self.response_prompt = PromptTemplate(
            input_variables=["caption", "context"],
            template="""You are a witty, personable AI assistant providing an instant, engaging response to an uploaded image.

Image Description: {caption}
Additional Context: {context}

Create a response that is:
- Clever and entertaining
- Tailored to the image's content
- Under 150 words
- Uses a conversational, friendly tone
- Compliments, jokes, or even a personality analysis 



Response:"""
        )

    def generate_detailed_response(self, caption):
        """
        Generate a sophisticated response using Gemini
        """
        if not self.gemini_model:
            return self.fallback_responses(caption)
        
        try:
            # Prepare context and get creative response
            context = self.get_additional_context(caption)
            
            # Use Langchain to generate response
            response_chain = self.response_prompt | self.gemini_model
            detailed_response = response_chain.invoke({
                "caption": caption,
                "context": context
            }).content
            
            return detailed_response
        except Exception as e:
            print(f"Error generating detailed response: {e}")
            return self.fallback_responses(caption)

    def get_additional_context(self, caption):
        """
        Generate additional context for more nuanced responses
        """
        context_options = [
            f"Exploring the intriguing elements of: {caption}",
            f"Diving deeper into the visual narrative of: {caption}",
            f"Unpacking the subtle details surrounding: {caption}"
        ]
        return random.choice(context_options)

    def fallback_responses(self, caption):
        """
        Fallback responses if Gemini model fails
        """
        fallback_templates = [
            f"Wow, check out this amazing scene: {caption}! 🌟",
            f"Breaking the internet with a snapshot of {caption}! 📸",
            f"If this image could talk, it would definitely say: '{caption}' 🗣️",
            f"Caught in 4K: A stunning moment of {caption}! 🔍"
        ]
        return random.choice(fallback_templates)

    def analyze_image(self, image_file):
        """
        Comprehensive image analysis method
        """
        if not self.captioner:
            return {'error': 'Image captioning model not loaded'}

        # Use tempfile for secure file handling
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            for chunk in image_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        try:
            # Perform image captioning
            captions = self.captioner(temp_file_path)
            
            # Get the primary caption
            primary_caption = captions[0]['generated_text']
            
            # Generate a detailed, creative response
            detailed_response = self.generate_detailed_response(primary_caption)

            return {
                'original_caption': primary_caption,
                'ai_response': detailed_response
            }
        
        finally:
            # Cleanup temporary file
            try:
                os.unlink(temp_file_path)
            except Exception as delete_error:
                print(f"Warning: Could not delete temp file {temp_file_path}: {delete_error}")

# Create a singleton instance of the agent
picture_perfect_agent = PicturePerfectAgent()

@csrf_exempt
def analyze_image_view(request):
    """
    Django view for image analysis
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    # Check if image is in request
    if 'image' not in request.FILES:
        return JsonResponse({'error': 'No image file uploaded'}, status=400)
    
    image_file = request.FILES['image']
    
    # Optional: File size validation
    if image_file.size > 10 * 1024 * 1024:  # 10MB max
        return JsonResponse({'error': 'Image file too large'}, status=400)
    
    try:
        # Analyze the image
        result = picture_perfect_agent.analyze_image(image_file)
        return JsonResponse(result)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def health_check(request):
    """
    Service health check endpoint
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'Picture Perfect Agent',
        'image_captioning_model': picture_perfect_agent.captioner is not None,
        'response_generation_model': picture_perfect_agent.gemini_model is not None
    })