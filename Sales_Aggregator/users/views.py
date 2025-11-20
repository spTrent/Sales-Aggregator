from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views import View

from .forms import CustomAuthenticationForm, CustomUserCreationForm


class RegisterView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect('home')
        form = CustomUserCreationForm()
        return render(request, 'users/register.html', {'form': form})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        return render(request, 'users/register.html', {'form': form})


class LoginView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect('home')
        form = CustomAuthenticationForm()
        return render(request, 'users/login.html', {'form': form})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username: str = form.cleaned_data.get('username')
            password: str = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_url: str = request.GET.get('next', 'home')
                return redirect(next_url)
        messages.error(request, 'Неверный логин или пароль')
        return render(request, 'users/login.html', {'form': form})


class LogoutView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        logout(request)
        return redirect('home')
