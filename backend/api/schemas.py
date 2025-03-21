from ninja import ModelSchema, Schema

from engine.models import Player, Game


class PlayerShow(ModelSchema):
    class Meta:
        model = Player
        fields = ['id', 'name', 'game']


class GameShow(ModelSchema):
    class Meta:
        model = Game
        fields = ['id', 'picture', 'status']


class GameTile(Schema):
    picture: str
    your_tile: str


class GameCurrentStatus(Schema):
    status: str = "WAITING"