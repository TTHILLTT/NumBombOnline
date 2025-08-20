from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.forms import ValidationError
from .models import User
from django import forms
from django.utils.translation import gettext_lazy as _


class UserCreationForm(BaseUserCreationForm):

    def clean_username(self):
        username = self.cleaned_data['username']

        # 检查用户名是否以数字开头
        if username and username[0].isdigit():
            raise ValidationError(_("The username cannot start with a number."))

        return super().clean_username()

    class Meta(BaseUserCreationForm.Meta):
        model = User
        fields = ('username', 'email')
