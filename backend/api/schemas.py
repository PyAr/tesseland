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

class GameList(Schema):
    id: str
    status: str
    players: list[PlayerShow]


class GameTile(Schema):
    picture: str
    figure: str


class GameCurrentStatus(Schema):
    status: str = "WAITING"