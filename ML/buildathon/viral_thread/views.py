from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from viral_thread.services import EnhancedViralThreadGenerator
class GenerateThreadView(APIView):
    def post(self, request):
        topic = request.data.get('topic')
        if not topic:
            return Response(
                {"error": "Topic is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            generator = EnhancedViralThreadGenerator()
            thread_data = generator.generate_thread(topic)
            return Response(thread_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )