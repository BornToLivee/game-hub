from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date


class Game(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(unique=True)
    release_year = models.IntegerField()
    genre = models.ForeignKey("Genre", on_delete=models.CASCADE)
    platform = models.ManyToManyField("Platform", related_name="games", blank=True)
    publisher = models.ForeignKey("Publisher", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="game_images")
    link = models.URLField(max_length=500, unique=True)
    players = models.ManyToManyField("Player", related_name="games", blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def get_average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return sum(rating.score for rating in ratings) / ratings.count()
        return 0


class Platform(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Rating(models.Model):
    player = models.ForeignKey("Player", on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="ratings")
    score = models.PositiveIntegerField()

    class Meta:
        unique_together = ("player", "game")

    def __str__(self):
        return f"{self.player.username} - {self.game.title} - {self.score}"


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(unique=True)
    image = models.ImageField(upload_to="genre_images", blank=True, null=True)

    def __str__(self):
        return self.name


class Publisher(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(unique=True)
    country = models.CharField(max_length=100)
    capitalization = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    image = models.ImageField(upload_to="publisher_images", blank=True, null=True)

    class Meta:
        ordering = ["capitalization"]

    def __str__(self):
        return self.name


class Player(AbstractUser):
    email = models.EmailField(unique=True, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    wishlist_games = models.ManyToManyField(
        Game, related_name="wishlisted_by", blank=True
    )
    completed_games = models.ManyToManyField(
        Game, related_name="completed_by", blank=True
    )

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            age = (
                today.year
                - self.date_of_birth.year
                - (
                    (today.month, today.day)
                    < (self.date_of_birth.month, self.date_of_birth.day)
                )
            )
            return age
        return None

    class Meta:
        verbose_name = "Player"
        verbose_name_plural = "Players"
