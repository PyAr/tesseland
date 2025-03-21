from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, File
from ninja.files import UploadedFile

from engine.models import Game, Player, GameStatus
from api.schemas import GameShow, PlayerShow, GameTile, GameCurrentStatus

api = NinjaAPI()

class GameNotPlayable(Exception):
    def __init__(self, message):
        self.message = message


@api.exception_handler(GameNotPlayable)
def game_not_playable(request, exc):
    return api.create_response(
        request,
        {"message": "Game is not playable"},
        status=400,
    )


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
    _player = Player.objects.create(
        name=player_name,
        game=Game.objects.get(id=game_id)
    )
    return _player


@api.get("/game/{game_id}/status", response=GameCurrentStatus)
def get_game_status(request, game_id: str):
    return get_object_or_404(Game, id=game_id)    


@api.get("/game/{game_id}/players/{player_name}", response=GameTile)
def playing(request, game_id: str, player_name: str):
    game = get_object_or_404(Game, id=game_id)
    if game.status != GameStatus.PLAYING:
        raise GameNotPlayable("Game is not playing" if game.status == GameStatus.WAITING else "Game is finished")
    
    player = get_object_or_404(Player, game=game, name=player_name)
    return GameTile(
        picture=game.get_public_url(),
        your_tile=player.get_public_url()
    )

@api.get("/game/{game_id}/start/", response=GameCurrentStatus)
def start(request, game_id: str):
    game = get_object_or_404(Game, id=game_id)
    if game.status != GameStatus.WAITING:
        raise GameNotPlayable("Game is not waiting" if game.status == GameStatus.PLAYING else "Game is finished")

    players = game.players.all()
    tiles = game.compute_tiles()
    
    for tile, player in zip(tiles, game.players.all()):
        player.your_tile = tile
        player.save()

    game.status = GameStatus.PLAYING
    game.save()
    return GameCurrentStatus(status=game.status)
