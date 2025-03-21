# Tesseland 1.0

a Tessenation company.


# Palyers UI

## Pantalla 1: Register

Registra un player a una sesión de juego.

Tres widgets:

- nombre del player
- Session ID
- Botón de "Register"

"Register" le pega a /session/<id>/register/ con el nombre del player

## Pantalla 2: Waiting...

Busy wait a /session/<id>/<player_name>/status hasta que responda con la figura que hay que mostrar.

## Pantalla 3: Game

Muestra la figura fullscreen.

# Engine

Gestión de Games por Django Admin. Pero con endpoints de gestión para una futura UI distinta.

* Crear Game: POST game/new
* Registrar un Player en un Game: ´POST game/<id>/register/<player_name>´ 
* Devolver el status de un Game, para un Player: ´GET game/<id>/status/<player_name>´
* Arrancar un Game: ´POST game/<id>/start´