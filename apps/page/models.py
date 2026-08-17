from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models

User = get_user_model()


class Page(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="page_user")
    title = models.CharField(max_length=100)
    description = models.TextField(validators=[MinLengthValidator(5), MaxLengthValidator(500)])
    html = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = "Pages"
        ordering = ["-created_at"]