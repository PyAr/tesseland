from django.contrib import admin

from engine.models import Game, Player, GamePlayer


class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'status')


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class GamePlayerAdmin(admin.ModelAdmin):
    list_display = ('game', 'player', 'figure')


admin.site.register(Game, GameAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(GamePlayer, GamePlayerAdmin)
