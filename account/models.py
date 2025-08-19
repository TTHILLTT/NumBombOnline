from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.

class User(AbstractUser):
    bio = models.TextField(blank=True, max_length=500)
    status = models.CharField(max_length=20, choices=[
        ('playing', '在游戏中'), 
        ('not_playing', '不在游戏中'), 
        ('ERROR', '错误'),
    ], default='not_playing')
    win_count = models.PositiveIntegerField(default=0)
    lose_count = models.PositiveIntegerField(default=0)
    language = models.CharField(max_length=10, choices=[
        ('zh-hans', '简体中文'), 
        ('zh-tw', '繁體中文'), 
        ('en-us', 'English'), 
        ('jp', '日本語')
    ], default='zh-hans')

    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="account_users",  # Unique name
        related_query_name="account_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="account_users",  # Unique name
        related_query_name="account_user_permission",
    )