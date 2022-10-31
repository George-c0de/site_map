from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from site_map.models import Profile, OrthokeratologyFixedDesignLenses, CustomizedOrthokeratologicalLenses
from django import forms


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']


class CreateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'


class CreateOrthokeratologyFixedDesignLensesForm(forms.ModelForm):
    class Meta:
        model = OrthokeratologyFixedDesignLenses
        fields = '__all__'


class CreateCustomizedOrthokeratologicalLensesForm(forms.ModelForm):
    class Meta:
        model = CustomizedOrthokeratologicalLenses
        fields = '__all__'
