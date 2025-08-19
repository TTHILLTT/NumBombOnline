from django import forms
from .models import Room
from django.utils.translation import gettext_lazy as _


class RoomForm(forms.ModelForm):
    name = forms.CharField(label=_("Room name"), max_length=100, initial=_("New room"))
    min_num = forms.IntegerField(label=_("Minimum number"), initial=1)
    max_num = forms.IntegerField(label=_("Maximum number"), initial=100)
    max_player = forms.IntegerField(label=_("Maximum players"), initial=20)
    step_time = forms.IntegerField(label=_("Step time (seconds)"), initial=30)

    class Meta:
        model = Room
        fields = ['name', 'min_num', 'max_num', 'max_player', 'step_time']
