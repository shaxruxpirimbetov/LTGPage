from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.response import Response
from .serializers import UserSerializer, UpdateUserSerializer, AdminUpdateUserSerializer, ResponseUserSerializer
from .permissions import IsMe

User = get_user_model()


class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all().order_by("id")

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.AllowAny()]  # registration
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserSerializer
        return ResponseUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ResponseUserSerializer(serializer.instance).data, status=201)


class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ResponseUserSerializer
        if self.request.user.is_superuser:
            return AdminUpdateUserSerializer
        return UpdateUserSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]
        return [IsMe()]