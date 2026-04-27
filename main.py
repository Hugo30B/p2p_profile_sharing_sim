import pygame
import time
import threading
import Pyro5.api
from config import *
from core.player import Player
from network.udp_node import UDPNode
from network.pyro_node import PyroServer
from ui.renderer import GameRenderer
from ui.character_creator import CharacterCreator

# Función de intercambio (petición con Pyro)
def intercambio(ip_vecino, puerto_vecino, neighbors_dict, target_id):
    """Llamada con Pyro5 para obtener el perfil real"""
    uri = f"PYRO:streetpass@{ip_vecino}:{puerto_vecino}"
    try:
        with Pyro5.api.Proxy(uri) as proxy:
            perfil = proxy.get_profile()
            # Actualizamos el vecino con sus datos reales, estos datos se añaden por encima (por ejemplo el campo revelado nunca existía)
            neighbors_dict[target_id].update({
                "skin_color": perfil["skin_color"],
                "shoes_color": perfil["shoes_color"],
                "pants_color": perfil["pants_color"],
                "tshirt_color": perfil["tshirt_color"],
                "glasses_type": perfil["glasses_type"],
                "hat_type": perfil["hat_type"],
                "nombre": perfil["nombre"],
                "revelado": True
            })
            print(f"Intercambio con {perfil['nombre']} exitoso!")
    except Exception as e:
        print(f"Error en intercambio con {ip_vecino}: {e}")
        if target_id in neighbors_dict:
            neighbors_dict[target_id]["revelado"] = False

mi_jugador = Player() # Instanciamos un jugador
vecinos = {} # Aquí el udp_node guarda toda la info que sabe de cada vecino y la función intercambio modifica los nodos implkicados
renderer = GameRenderer(800, 600)
pygame.display.set_caption(f"Intercambio P2P")

# Pantalla de creación usando el nuevo módulo
creator = CharacterCreator(renderer)
creator.run(mi_jugador)

clock = pygame.time.Clock()

# Arrancamos el servidor Pyro que emite (es un hilo)
pyro_server = PyroServer(mi_jugador) # El servidor Pyro tiene la info de la instancia que hemos hecho
pyro_server.start()

# Arrancamos el servidor UDP (hilos (2) que emiten y reciben)
udp_node = UDPNode(mi_jugador, vecinos)
udp_node.start()

# --- Bucle Principal ---
running = True
while running:
    # Gestión de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movimiento
    dx, dy = 0, 0
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]: dx = -5
    if keys[pygame.K_d]: dx = 5
    if keys[pygame.K_w]: dy = -5
    if keys[pygame.K_s]: dy = 5
    mi_jugador.move(dx, dy, 800, 600)

    # Vecinos
    ahora = time.time()
    for v_id, v_data in list(vecinos.items()):
        # Borrar si se desconecta uno
        if ahora - v_data.get("last_seen", 0) > NEIGHBOR_TIMEOUT:
            del vecinos[v_id]
            continue

        # Proximidad
        v_pos = v_data["pos"]
        dist = ((mi_jugador.x - v_pos[0])**2 + (mi_jugador.y - v_pos[1])**2)**0.5
        
        if dist < PROXIMITY_THRESHOLD and not v_data.get("revelado"):
            v_data["revelado"] = "proceso" 
            threading.Thread(
                target=intercambio, 
                args=(v_data["ip"], v_data["pyro_port"], vecinos, v_id),
                daemon=True
            ).start() # Usamos un thread para que no se quede pillado el juego

    # Renderizado con la clase render
    renderer.render(mi_jugador, vecinos)
    clock.tick(60)

pygame.quit()
