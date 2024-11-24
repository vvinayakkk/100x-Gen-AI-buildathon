from rest_framework import serializers
from .models import Celebrity, Impersonation

class CelebritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Celebrity
        fields = '__all__'

class ImpersonationSerializer(serializers.ModelSerializer):
    celebrity_name = serializers.CharField(source='celebrity.name', read_only=True)
    
    class Meta:
        model = Impersonation
        fields = ['id', 'celebrity_name', 'input_tweet', 'response', 'created_at']