from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .meme_generator import MemeGenerator
from django.conf import settings
import os

@api_view(['POST'])
def generate_meme(request):
    try:
        input_text = request.data.get('input_text')
        if not input_text:
            return Response({'error': 'No input text provided'}, status=400)

        generator = MemeGenerator(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            imgflip_username=os.getenv('IMGFLIP_USERNAME'),
            imgflip_password=os.getenv('IMGFLIP_PASSWORD')
        )

        result = generator.generate_complete_meme(input_text)
        return Response(result)

    except Exception as e:
        return Response({'error': str(e)}, status=500)