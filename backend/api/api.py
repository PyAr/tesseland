from django.core.files.images import ImageFile
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from PIL import Image
from io import BytesIO
from ninja import NinjaAPI, File
from ninja.files import UploadedFile

from engine.models import Game, Player, GameStatus
from api.schemas import GameShow, PlayerShow, GameTile, GameCurrentStatus, GameList

api = NinjaAPI()

class GameNotPlayable(Exception):
    def __init__(self, message):
        self.message = message


class GameAlreadyStarted(Exception):
    def __init__(self, message):
        self.message = message

@api.exception_handler(GameNotPlayable)
@api.exception_handler(GameAlreadyStarted)
def game_not_playable(request, exc):
    return api.create_response(
        request,
        {"message": exc.message},
        status=400,
    )


@api.get("/game", response=list[GameList])
def get_games(request):
    return Game.objects.filter(status=GameStatus.WAITING)


@api.post("/game", response=GameShow)
def create_game(request, game_id: str, file: UploadedFile = File(...)):
    _game = Game.objects.create(
        id=game_id, 
        picture=file, 
        status=GameStatus.WAITING
    )
    return _game


@api.post("/game/{game_id}/register/{player_name}", response=PlayerShow)
def register_player(request, game_id: str, player_name: str):
    try:
        return Player.objects.get(game=game_id, name=player_name)
    except Player.DoesNotExist:
        game = get_object_or_404(Game, id=game_id, status=GameStatus.WAITING)
        _player = Player.objects.create(
            name=player_name,
            game=game
        )
        return _player
    

@api.get("/game/{game_id}/status", response=GameCurrentStatus)
def get_game_status(request, game_id: str):
    return get_object_or_404(Game, id=game_id)    


@api.get("/game/{game_id}/players/{player_name}", response=GameTile)
def playing(request, game_id: str, player_name: str):
    game = get_object_or_404(Game, id=game_id)
    # Temporal disabled
    # if game.status != GameStatus.PLAYING:
    #     raise GameNotPlayable("Game is not playing" if game.status == GameStatus.WAITING else "Game is finished")
    
    player = get_object_or_404(Player, game=game, name=player_name)
    return GameTile(
        picture=game.get_public_url(),
        figure=player.get_public_url()
    )

@api.post("/game/{game_id}/start/", response=GameCurrentStatus)
def start(request, game_id: str):
    game = get_object_or_404(Game, id=game_id)
    if game.status != GameStatus.WAITING:
        raise GameAlreadyStarted("Game is playing!!")

    players = game.players.all()
    tiles = game.compute_tiles()
    
    for tile, player in zip(tiles, players):
        image = Image.fromarray(tile)
        buffer = BytesIO()
        image.save(buffer, format="PNG")

        player.figure = ImageFile(file=buffer, name=f"{player.game.id}_{player.name}.png")  # hojaldre con el nombre del archivo
        player.save()

    game.status = GameStatus.PLAYING
    game.save()
    return GameCurrentStatus(status=game.status)
