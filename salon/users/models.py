from django.contrib.auth.models import AbstractUser
from django.urls import reverse


class User(AbstractUser):
    def get_absolute_url(self):
        return reverse("users:edit_profile")
    
    def get_short_name(self):
        """Возвращает имя или username, если имя не заполнено"""
        return self.first_name or self.username