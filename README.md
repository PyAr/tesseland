# Tesseland 1.0

a Tessenation company.


# Front

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