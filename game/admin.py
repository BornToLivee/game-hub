from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Game,
    Genre,
    Platform,
    Player,
    Publisher,
)


@admin.register(Player)
class PlayerAdmin(UserAdmin):
    list_display = UserAdmin.list_display + (
        "email",
        "first_name",
        "last_name",
    )
    fieldsets = UserAdmin.fieldsets + (
        (
            (
                "Additional info",
                {
                    "fields": (
                        "age",
                        "completed_games",
                        "wishlist_games",
                    )
                },
            ),
        )
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            (
                "Additional info",
                {
                    "fields": (
                        "first_name",
                        "last_name",
                        "email",
                        "age",
                    )
                },
            ),
        )
    )


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    search_fields = ("title",)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    search_fields = ("title",)


admin.site.register(Genre)

admin.site.register(Platform)
