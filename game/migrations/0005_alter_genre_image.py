# Generated by Django 5.0.6 on 2024-07-16 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("game", "0004_remove_player_age_player_date_of_birth"),
    ]

    operations = [
        migrations.AlterField(
            model_name="genre",
            name="image",
            field=models.ImageField(
                blank=True,
                default="media/genre_images/default.jpg",
                null=True,
                upload_to="genre_images",
            ),
        ),
    ]
