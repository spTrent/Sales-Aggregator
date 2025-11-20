from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Придумайте логин'}
        ),
        label='Логин',
        help_text='Обязательное поле. Только буквы, цифры и @/./+/-/_',
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Придумайте пароль'}
        ),
        label='Пароль',
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Повторите пароль'}
        ),
        label='Подтверждение пароля',
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2')


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите ваш логин'}
        ),
        label='Логин',
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Введите ваш пароль',
            }
        ),
        label='Пароль',
    )
