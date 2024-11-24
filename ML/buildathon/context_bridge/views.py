from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TweetProcessorSerializer
from .tweet_processor import FlexibleTweetProcessor

class ProcessTweetView(APIView):
    def post(self, request):
        serializer = TweetProcessorSerializer(data=request.data)
        if serializer.is_valid():
            processor = FlexibleTweetProcessor()
            result = processor.process_tweet(
                serializer.validated_data['tweet'],
                serializer.validated_data['instructions']
            )
            return Response({'result': result}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
