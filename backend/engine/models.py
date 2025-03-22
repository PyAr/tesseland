from django.db import models
from django.conf import settings

from engine.tiles import get_tiles


class GameStatus(models.TextChoices):
    WAITING = 'WAITING'
    PLAYING = 'PLAYING'
    FINISHED = 'FINISHED'


class Game(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    picture = models.ImageField(upload_to='games')
    status = models.CharField(max_length=10, choices=GameStatus.choices)

    def __str__(self):
        return self.id

    def get_public_url(self):
        return settings.MEDIA_URL + self.picture.name
    
    def compute_tiles(self):
        return get_tiles(self.picture.path, self.players.count())
    
    def get_owner(self):
        return self.players.filter(is_owner=True).first()
        
        
class Player(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='players' )
    is_owner = models.BooleanField(default=False)
    figure = models.ImageField(upload_to='figures', null=True, blank=True)

    class Meta:
        unique_together = ('game', 'name')
    
    def get_public_url(self):
        return settings.MEDIA_URL + self.figure.name

    def __str__(self):
        return f'{self.game.id} - {self.name}'
