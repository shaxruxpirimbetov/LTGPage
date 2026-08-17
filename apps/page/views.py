from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.user.permissions import IsMine
from .models import Page
from .serializers import PageSerializer, CreatePageSerializer

User = get_user_model()

class PageListCreateAPIView(generics.ListCreateAPIView):
    def get_queryset(self):
        filters = self.request.GET
        if filters.get("user"):
            user = User.objects.filter(username=filters["user"]).first()
            if not user:
                return []
            return Page.objects.filter(user=user)
        return Page.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return PageSerializer
        return CreatePageSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        return Response(PageSerializer(serializer.instance).data, status=201)


class PageDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Page.objects.all()
    serializer_class = PageSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [IsMine()]


class PageView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, pk):
        page = Page.objects.filter(id=pk).first()
        if not page:
            return HttpResponse("<h1>Page Not Found</h1>",status=404)
        return HttpResponse(page.html)
