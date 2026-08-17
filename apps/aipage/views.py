from rest_framework import generics, permissions
from rest_framework.response import Response
from apps.user.permissions import IsMine
from utils import ai
from .models import AIPage
from .serializers import AIPageSerializer, CreateAIPageSerializer


class AIPageListCreateAPIView(generics.ListCreateAPIView):
    queryset = AIPage.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateAIPageSerializer
        return AIPageSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        serializer.instance.html = ai.generate_html(serializer.instance.prompt)
        serializer.instance.save()
        return Response(AIPageSerializer(serializer.instance).data, status=201)


class AIPageDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AIPage.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return AIPageSerializer
        return AIPageSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [IsMine()]