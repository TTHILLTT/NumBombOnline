from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import User

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
        if User.objects.filter(username=username).exists():
            return HttpResponse("Username already exists")
        if User.objects.filter(email=email).exists():
            return HttpResponse("Email already exists")
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        login(request, user)
        return redirect('index')
    return render(request,'register.html')
