# Tesseland 1.0

a Tesselnation company.

# Como utilizarlo

Para configurar la aplicación por primera vez se deben correr las migraciones

```sh
> uv run backend/manage.py migrate
```

Después para levantar el servidor: 

```sh
> uv run backend/manage.py runserver 0.0.0.0:8000
```

# Players UI

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

Mientras se hace click en la pantalla, reemplaza la figura con la imagen completa.

# Engine

Gestión de Games por Django Admin. Pero con endpoints de gestión para una futura UI distinta.

* Crear Game: POST game/new
* Registrar un Player en un Game: ´POST game/<id>/register/<player_name>´ 
* Devolver el status de un Game, para un Player: ´GET game/<id>/status/<player_name>´
* Arrancar un Game: ´POST game/<id>/start´

# ToDO List

* Fin del juego: declarar el fin y determinar el resultado.
* AuthN/Z de admin y players.
* Pantallas de admin (replace Django admin).
* Dyamic game: con cada registro se re-genera el teselado y se re-distribuyen las figuras entre los players.
* Server-side events: para reemplazar el busy-wait antes de empezar el juego.
* Video: permitir armar videos, no solo imágenes estáticas.
* UI enhancements: infinitas cosas para hacer.
    * Mostrar imagen completa a los usuarios.