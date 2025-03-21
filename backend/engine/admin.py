from django.contrib import admin

from engine.models import Game, Player


class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'status')


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


admin.site.register(Game, GameAdmin)
admin.site.register(Player, PlayerAdmin)
