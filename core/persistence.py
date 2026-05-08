import argparse
import json
import os
from core.player import Player

DEFAULT_PROFILE = "default_profile.json"

def get_player_from_args():
    """
    Analiza los argumentos de línea de comandos para cargar un perfil.
    Retorna una tupla (instancia_player, ruta_archivo).
    """
    parser = argparse.ArgumentParser(description="P2P Profile Sharing Sim")
    parser.add_argument(
        "--perfil", 
        type=str, 
        help="Ruta al archivo JSON del perfil del jugador",
        default=None
    )
    
    args, unknown = parser.parse_known_args()
    
    # Intentar cargar el archivo
    if args.perfil and os.path.exists(args.perfil):
        try:
            with open(args.perfil, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"Perfil cargado desde {args.perfil}")
                return Player.from_dict(data), args.perfil
        except Exception as e:
            print(f"No se pudo cargar el perfil: {e}. Creando uno nuevo.")
    
    # Si no se especificó o no existe, crear jugador nuevo
    player = Player()
    
    # nombre del archivo basado en el ID si no se pasó por argumento
    filepath = args.perfil if args.perfil else f"{player.id[:4]}_profile.json"
    
    if args.perfil and not os.path.exists(args.perfil):
        print(f"{args.perfil} no encontrado. Se creará al salir.")
    else:
        print(f"Nuevo perfil. Se guardará en {filepath} al salir.")
        
    return player, filepath

def guardar_jugador(player, filepath):
    """
    Guarda los datos del jugador en un archivo JSON.
    """
    try:
        data = player.to_dict()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"Perfil guardado correctamente en {filepath}")
    except Exception as e:
        print(f"No se pudo guardar el perfil: {e}")
