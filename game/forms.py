from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Player


class PlayerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    age = forms.IntegerField(required=False)

    class Meta:
        model = Player
        fields = ["username", "email", "age", "password1", "password2"]