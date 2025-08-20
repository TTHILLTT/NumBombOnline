from django.db import models
from account.models import User
from django.utils.translation import gettext_lazy as _


# Create your models here.

class Room(models.Model):
    name = models.CharField(_('room name'), max_length=127) # 房间名称
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, verbose_name=_('owner')) # 房主
    min_num = models.PositiveIntegerField(_('minimum number'), default=1) # 最小数字
    max_num = models.PositiveIntegerField(_('maximum number'), default=100) # 最大数字
    max_player = models.PositiveIntegerField(_('maximum player number'), default=20) # 最大玩家数
    players = models.ManyToManyField(User, related_name='room_players', blank=True, verbose_name=_('players')) # 玩家列表
    hide_room = models.BooleanField(_('hide room'), default=False) # 是否隐藏房间
    created_at = models.DateTimeField(_('created at'), auto_now_add=True) # 创建时间
    updated_at = models.DateTimeField(_('updated at'), auto_now=True) # 更新时间
    room_code = models.CharField(_('room code'), max_length=127, unique=True, blank=True, null=True) # 房间码
    step_time = models.PositiveIntegerField(_('step time limit'), default=30) # 玩家每步时间限制
    current_player = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='current_player', verbose_name=_('current player')) # 当前玩家
    order = models.JSONField(_('player order'), default=list) # 玩家顺序
    status = models.CharField(_('room status'), max_length=20, choices=[
        ('joining', '加入中'), 
        ('ordering', '排序中'), 
        ('preparing', '准备中'),
        ('playing', '进行中'),
        ('end', '结束'),
        ('ERROR', '错误'),
    ], default='not_playing')
    active = models.BooleanField(_('active'), default=True) # 是否活跃

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('room')
        verbose_name_plural = _('rooms')
