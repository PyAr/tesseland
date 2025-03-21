from ninja import NinjaAPI, File
from ninja.files import UploadedFile

from engine.models import Game, Player, GamePlayer, GameStatus
from api.schemas import GameShow, PlayerShow, GameTile, GameCurrentStatus

api = NinjaAPI()


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
    try:
        return GameCurrentStatus(detail=Game.objects.get(id=game_id).status)
    except Game.DoesNotExist:
        return GameCurrentStatus(detail="Game not found")


@api.get("/game/{game_id}/players/{player_name}", response=GameTile | GameCurrentStatus)
def playing(request, game_id: str, player_name: str):
    try:
        game = Game.objects.get(id=game_id)
        if game.status != GameStatus.PLAYING:
            return GameCurrentStatus(detail="Game is not playing" if game.status == GameStatus.WAITING else "Game is finished")
        
        player = Player.objects.get(game=game, name=player_name)
        game_player = GamePlayer.objects.get(game=game, player=player)
        return GameTile(
            picture=game.get_public_url(),
            your_tile=game_player.get_public_url()
        )
    except Game.DoesNotExist:
        return GameCurrentStatus(detail="Game not found")
    except Player.DoesNotExist:
        return GameCurrentStatus(detail="Player not found")
    except GamePlayer.DoesNotExist:
        return GameCurrentStatus(detail="Game player not found")


@api.get("/game/{game_id}/start/", response=GameCurrentStatus)
def start(request, game_id: str):
    try:
        game = Game.objects.get(id=game_id)
        # Check status, solo arranca si està waiting, sino error o algo.

        # Genera los tiles, tantos como Players tenga el game
        # Asigna tiles a los GamePlayers
        # Cambia el status del game
        # devuelve status nuevo
        players = game.players.all()
        tiles = game.compute_tiles()
        # check len de las cosas
        for tile, player in zip(tiles, game.players.all()):
            player.your_tile = tile
            player.save()

        game.status = GameStatus.PLAYING
        game.save()
        return GameCurrentStatus(detail=game.status)

    except Game.DoesNotExist:
        return GameCurrentStatus(detail="Game not found")
    except Player.DoesNotExist:  # ???
        return GameCurrentStatus(detail="Player not found")