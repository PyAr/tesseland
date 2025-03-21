from django.db import models


class GameStatus(models.TextChoices):
    WAITING = 'WAITING'
    PLAYING = 'PLAYING'
    FINISHED = 'FINISHED'


class Player(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=10, unique=True)


class Game(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    picture = models.ImageField(upload_to='games')
    status = models.CharField(max_length=10, choices=GameStatus.choices)


class GamePlayer(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    figure = models.ImageField(upload_to='figures')
