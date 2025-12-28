from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Обязательно. Должен быть уникальным."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует.")
        return email


class EditUserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")
