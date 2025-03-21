from django.db import models
from django.conf import settings


class GameStatus(models.TextChoices):
    WAITING = 'WAITING'
    PLAYING = 'PLAYING'
    FINISHED = 'FINISHED'


class Game(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    picture = models.ImageField(upload_to='games')
    status = models.CharField(max_length=10, choices=GameStatus.choices)

    def get_public_url(self):
        return settings.MEDIA_URL + self.picture.name


class Player(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=10, unique=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='players')


class GamePlayer(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    figure = models.ImageField(upload_to='figures')

    def get_public_url(self):
        return settings.MEDIA_URL + self.figure.name
