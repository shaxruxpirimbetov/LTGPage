from django.urls import path
from . import views

urlpatterns = [
    path("", views.PageListCreateAPIView.as_view()),
    path("<int:pk>/", views.PageDetailAPIView.as_view()),
    path("view/<int:pk>/", views.PageView.as_view()),
]