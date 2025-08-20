from django.contrib import admin
from .models import Room
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


# Register your models here.


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner_link', 'min_num', 'max_num', 'max_player', 'hide_room', 'created_at', 'updated_at', 'room_code', 'step_time', 'current_player', 'order', 'status', 'active')

    def owner_link(self, obj: Room):
        if obj.owner:
            # 生成指向 Owner 详情页的链接
            url = reverse('admin:game_room_change', args=[obj.owner.id])
            return format_html('<a href="{}">{}</a>', url, obj.owner.username)
        else:
            return '-'

    owner_link.short_description = _('owner')  # 设置列表列标题
