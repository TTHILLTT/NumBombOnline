from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _


# Create your models here.

class User(AbstractUser):
    bio = models.TextField(_('bio'), blank=True, max_length=500)
    status = models.CharField(_('status'), max_length=20, choices=[
        ('playing', '在游戏中'),
        ('not_playing', '不在游戏中'),
        ('ERROR', '错误'),
    ], default='not_playing')
    win_count = models.PositiveIntegerField(_('win count'), default=0)
    lose_count = models.PositiveIntegerField(_('lose count'), default=0)
