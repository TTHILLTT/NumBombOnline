from django.db import models
from account.models import User


# Create your models here.

class Room(models.Model):
    name = models.CharField(max_length=127) # 房间名称
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True) # 房主
    min_num = models.PositiveIntegerField(default=0) # 最小数字
    max_num = models.PositiveIntegerField(default=0) # 最大数字
    max_player = models.PositiveIntegerField(default=0) # 最大玩家数
    players = models.ManyToManyField(User, related_name='room_players', blank=True) # 玩家列表
    hide_room = models.BooleanField(default=False) # 是否隐藏房间
    created_at = models.DateTimeField(auto_now_add=True) # 创建时间
    updated_at = models.DateTimeField(auto_now=True) # 更新时间
    room_code = models.CharField(max_length=127, unique=True, blank=True) # 房间码
    step_time = models.PositiveIntegerField(default=30) # 玩家每步时间限制
    current_player = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='current_player') # 当前玩家
    order = models.JSONField(default=list) # 玩家顺序