from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Player
from .models import Rating


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score']
        widgets = {
            'score': forms.NumberInput(attrs={'min': 1, 'max': 10}),
        }


class PlayerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    age = forms.IntegerField(required=False)

    class Meta:
        model = Player
        fields = ["username", "email", "age", "password1", "password2"]