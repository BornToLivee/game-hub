from datetime import timedelta

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import DateInput
from django.utils import timezone

from game.models import (
    Game,
    Genre,
    Platform,
    Player,
    Publisher,
    Rating,
)


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ["score"]
        widgets = {
            "score": forms.NumberInput(attrs={"min": 1, "max": 10}),
        }


class GameCreateForm(forms.ModelForm):
    platform = forms.ModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Game
        fields = (
            "title",
            "description",
            "platform",
            "release_year",
            "genre",
            "publisher",
            "image",
            "link",
        )


class GameSearchForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by title"}),
    )


class PlayerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=False)
    date_of_birth = forms.DateField(
        widget=DateInput(attrs={"type": "date"}), required=False
    )
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    class Meta:
        model = Player
        fields = [
            "username",
            "email",
            "date_of_birth",
            "first_name",
            "last_name",
            "password1",
            "password2",
        ]

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get("date_of_birth")
        if date_of_birth:
            today = timezone.now().date()
            min_age = today - timedelta(days=365 * 100)
            max_age = today - timedelta(days=365 * 5)
            if not (min_age <= date_of_birth <= max_age):
                raise forms.ValidationError(
                    f"Date of birth must be between {min_age} and {max_age}."
                )
        return date_of_birth


class PlayerUpdateForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ["first_name", "last_name", "date_of_birth"]


class GenreCreateForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = "__all__"


class PublisherCreateForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = "__all__"
