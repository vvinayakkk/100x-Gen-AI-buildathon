from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from .models import Celebrity, Impersonation
from .serializers import CelebritySerializer, ImpersonationSerializer
from .agents import CelebrityImpersonationAgent

class CelebrityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Celebrity.objects.all()
    serializer_class = CelebritySerializer

class ImpersonationViewSet(viewsets.ModelViewSet):
    queryset = Impersonation.objects.all()
    serializer_class = ImpersonationSerializer

@api_view(['POST'])
def generate_impersonation(request):
    try:
        celebrity_id = request.data.get('celebrity_id')
        tweet = request.data.get('tweet')
        
        if not celebrity_id or not tweet:
            return Response(
                {'error': 'Both celebrity_id and tweet are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        celebrity = Celebrity.objects.get(id=celebrity_id)
        
        # Initialize the impersonation agent
        agent = CelebrityImpersonationAgent(
            api_key=settings.GOOGLE_API_KEY,
            temperature=0.7
        )
        
        # Generate response
        celebrity_data = {
            'name': celebrity.name,
            'background': celebrity.background,
            'tone': celebrity.tone,
            'speaking_style': celebrity.speaking_style,
            'emotional_range': celebrity.emotional_range,
            'example_tweets': celebrity.example_tweets
        }
        
        response = agent.impersonate(tweet, celebrity_data)
        
        # Save the impersonation
        impersonation = Impersonation.objects.create(
            celebrity=celebrity,
            input_tweet=tweet,
            response=response
        )
        
        serializer = ImpersonationSerializer(impersonation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Celebrity.DoesNotExist:
        return Response(
            {'error': 'Celebrity not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )