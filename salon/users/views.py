from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib import messages

from .forms import CustomUserCreationForm, EditUserProfileForm

User = get_user_model()


class UserCreateView(CreateView):
    """Регистрация нового клиента"""
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm
    # После регистрации — сразу в личный кабинет (а не на логин)
    success_url = reverse_lazy("bookings:my_bookings")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(
            self.request,
            f"Добро пожаловать, {user.get_short_name() or user.username}! "
            "Вы успешно зарегистрировались."
        )
        # Перенаправляем в личный кабинет
        return redirect(self.success_url)


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля клиента"""
    model = User
    form_class = EditUserProfileForm
    template_name = "users/profile_edit.html"  # ← обновлён путь к шаблону

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        messages.success(self.request, "Профиль успешно обновлён.")
        return reverse_lazy("users:profile_edit")

    def form_invalid(self, form):
        messages.error(self.request, "Пожалуйста, исправьте ошибки в форме.")
        return super().form_invalid(form)