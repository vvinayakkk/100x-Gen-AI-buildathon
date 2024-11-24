from rest_framework import serializers

class TweetProcessorSerializer(serializers.Serializer):
    tweet = serializers.CharField(required=True)
    instructions = serializers.CharField(required=True)
