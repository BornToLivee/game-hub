from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Player, Game, Platform
from .models import Rating


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score']
        widgets = {
            'score': forms.NumberInput(attrs={'min': 1, 'max': 10}),
        }


class GameForm(forms.ModelForm):
    platforms = forms.ModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Game
        fields = ("title", "description", "release_year", "platforms", "genre", "publisher", "image", "link",)


class GameSearchForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by title"}),
    )


class PlayerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    age = forms.IntegerField(required=False)

    class Meta:
        model = Player
        fields = ["username", "email", "age", "password1", "password2"]