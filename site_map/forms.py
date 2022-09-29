from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.forms import ModelForm, NumberInput

from site_map.models import Profile
from django import forms


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']


class CreateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['user', 'card', 'photo', 'patronymic']
