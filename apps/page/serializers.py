from rest_framework import serializers
from apps.user.serializers import ResponseUserSerializer
from .models import Page

class PageSerializer(serializers.ModelSerializer):
    user = ResponseUserSerializer(read_only=True)
    class Meta:
        model = Page
        fields = "__all__"


class CreatePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ["title", "description", "html"]