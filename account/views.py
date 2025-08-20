from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import User
from .forms import UserCreationForm
from django.urls import reverse_lazy

import re

# Create your views here.


def user_logout(request):
    logout(request)
    return redirect('index')


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'register.html', {'form': form})
    return render(request, 'register.html', {'form': UserCreationForm()})


def profile(request, username: str = None):
    if not username:
        if not request.user.is_authenticated:
            return redirect('login')
        username = request.user.username
        return redirect('profile_username', username=username)
    if username.isdigit():
        user = User.objects.get(id=username)
        return redirect('profile_username', username=user.username)
    else:
        user = User.objects.get(username=username)
        return render(request, 'profile.html', {'user': user})
