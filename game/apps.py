from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GameConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'game'
    verbose_name = _('Game')
    