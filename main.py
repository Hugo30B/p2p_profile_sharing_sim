import pygame
from core.player import Player
from core.social_controller import SocialController
from core.game_loop import run_game_loop
from network.udp_node import UDPNode
from network.pyro_node import PyroServer
from ui.renderer import GameRenderer
from ui.character_creator import CharacterCreator
from ui.social_ui import SocialUI

mi_jugador = Player()
vecinos = {}
renderer = GameRenderer(800, 600)
pygame.display.set_caption("Intercambio P2P")

creator = CharacterCreator(renderer)
creator.run(mi_jugador)

social_controller = SocialController(mi_jugador, vecinos)
social_ui = SocialUI(mi_jugador)

pyro_server = PyroServer(mi_jugador, social_controller)
pyro_server.start()

udp_node = UDPNode(mi_jugador, vecinos)
udp_node.start()

run_game_loop(mi_jugador, vecinos, renderer, social_controller, social_ui)
