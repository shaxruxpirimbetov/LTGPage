from rest_framework import serializers
from apps.user.serializers import ResponseUserSerializer
from .models import AIPage

class AIPageSerializer(serializers.ModelSerializer):
    user = ResponseUserSerializer(read_only=True)
    class Meta:
        model = AIPage
        fields = '__all__'


class CreateAIPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIPage
        fields = ["id", "title", "description", "prompt"]