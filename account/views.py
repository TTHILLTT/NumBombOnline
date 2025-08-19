from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import User
import re


def is_valid_username(username):
    if len(username) < 4 or len(username) > 20:
        return False
    if not re.match(r'^[a-zA-Z一-龟_][a-zA-Z0-9一-龟_]+$', username):
        return False
    return True


def is_valid_email(email):
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return False
    return True

# Create your views here.


def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        else:
            return HttpResponse("Invalid login")
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('index')


def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if is_valid_username(username) == False:
            return HttpResponse("Invalid username")
        if is_valid_email(email) == False:
            return HttpResponse("Invalid email")
        if User.objects.filter(username=username).exists():
            return HttpResponse("Username already exists")
        if User.objects.filter(email=email).exists():
            return HttpResponse("Email already exists")
        user = User.objects.create_user(
            username=username, email=email, password=password)
        user.save()
        login(request, user)
        return redirect('index')
    return render(request, 'register.html')


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
