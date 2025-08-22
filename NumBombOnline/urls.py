"""
URL configuration for NumBombOnline project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
import game.views
import account.views
from django.contrib.auth.views import LoginView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', game.views.index, name='index'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', account.views.user_logout, name='logout'),
    path('register/', account.views.register, name='register'),
    path('profile/', account.views.profile, name='profile'),
    path('accounts/profile/', lambda request: redirect('profile')),
    path('profile/<str:username>/', account.views.profile, name='profile_username'),
    path('change-bio/', account.views.change_bio, name='change_bio'),
    path('room/create/', game.views.room_create, name='room_create'),
    path('room/detail/<int:room_id>/', game.views.room_detail, name='room_detail'),
    path('room/spectate/<int:room_id>/', game.views.room_spectate, name='room_spectate'),
    path('room/play/<int:room_id>/', game.views.room_play, name='room_play'),
    path('ws-echo-test/', game.views.ws_echo_test, name='ws_echo_test'),
    path('about/', game.views.about, name='about')
]
