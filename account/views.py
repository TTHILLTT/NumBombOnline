from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import User
from .forms import UserChangeBioForm, UserCreationForm
from django.urls import reverse_lazy 
from django.contrib.auth.decorators import login_required

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

@login_required
def change_bio(request):
    if request.method == "POST":
        form = UserChangeBioForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile_username', username=request.user.username)
        else:
            return render(request, 'change_bio.html', {'form': form})
    else:
        form = UserChangeBioForm(instance=request.user)
        return render(request, 'change_bio.html', {'form': form})