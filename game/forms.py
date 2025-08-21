from django import forms
from .models import Room
from django.utils.translation import gettext_lazy as _


class RoomForm(forms.ModelForm):
    name = forms.CharField(label=_("Room name"), max_length=100, initial=_("New room"))
    min_num = forms.IntegerField(label=_("Minimum number"), initial=1)
    max_num = forms.IntegerField(label=_("Maximum number"), initial=100)
    max_player = forms.IntegerField(label=_("Maximum players"), initial=20)
    step_time = forms.IntegerField(label=_("Step time (seconds)"), initial=30)

    def clean(self):
        cleaned_data = super().clean()
        min_num = cleaned_data.get('min_num')
        max_num = cleaned_data.get('max_num')
        if min_num > max_num:
            raise forms.ValidationError(_("Minimum number should be less than or equal to maximum number."))
        return cleaned_data

    class Meta:
        model = Room
        fields = ['name', 'min_num', 'max_num', 'max_player', 'step_time']
