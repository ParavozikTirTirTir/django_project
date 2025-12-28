from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views

app_name = "users"

urlpatterns = [
    # Регистрация
    path(
        "signup/",
        views.UserCreateView.as_view(),
        name="signup"  # ← единый стандарт: signup, login, logout
    ),

    # Стандартные URL аутентификации (login, logout)
    path("", include("django.contrib.auth.urls")),
]
