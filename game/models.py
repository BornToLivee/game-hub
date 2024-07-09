from django.contrib.auth.models import AbstractUser
from django.db import models


GAME_PLATFORMS = [
    ("PS3", "PlayStation 3"),
    ("PS4", "PlayStation 4"),
    ("PS5", "PlayStation 5"),
    ("XBox 360", "Xbox 360"),
    ("XBox One", "Xbox One"),
    ("PC", "Personal Computer"),
    ("Switch", "Nintendo Switch"),
]


class Game(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(unique=True)
    release_year = models.IntegerField()
    platform = models.CharField(max_length=100, choices=GAME_PLATFORMS)
    genre = models.ForeignKey("Genre", on_delete=models.DO_NOTHING)
    publisher = models.ForeignKey("Publisher", on_delete=models.CASCADE)
    user_scores = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    image = models.ImageField(upload_to="game_images")
    link = models.URLField(max_length=500, unique=True)
    players = models.ManyToManyField("Player", related_name="games")

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def get_average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return sum(rating.score for rating in ratings) / ratings.count()
        return 0


class Rating(models.Model):
    player = models.ForeignKey("Player", on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='ratings')
    score = models.PositiveIntegerField()

    class Meta:
        unique_together = ('player', 'game')

    def __str__(self):
        return f'{self.player.username} - {self.game.title} - {self.score}'


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
    age = models.IntegerField(null=True, blank=True)
    wishlist_games = models.ManyToManyField(Game, related_name="wishlisted_by", blank=True)
    completed_games = models.ManyToManyField(Game, related_name="completed_by", blank=True)

    class Meta:
        verbose_name = "Player"
        verbose_name_plural = "Players"
