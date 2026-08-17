from django.urls import path
from . import views

urlpatterns = [
    path("", views.AIPageListCreateAPIView.as_view()),
    path("<int:pk>/", views.AIPageDetailAPIView.as_view()),
]