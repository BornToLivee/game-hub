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
    platform = forms.ModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Game
        fields = ("title", "description", "platform", "release_year", "genre", "publisher", "image", "link",)


class GameSearchForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by title"}),
    )


class PlayerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=False)
    age = forms.IntegerField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    class Meta:
        model = Player
        fields = ["username", "email", "age", "first_name", "last_name", "password1", "password2",]


class PlayerUpdateForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['first_name', 'last_name', 'age']