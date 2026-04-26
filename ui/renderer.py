import pygame
from config import PROXIMITY_THRESHOLD

class GameRenderer:
    def __init__(self, screen_width, screen_height):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.font = pygame.font.SysFont(None, 24)
        self.bg_color = (240, 240, 240)
        self.player_radius = 20

    def render(self, player, neighbors):
        """Dibuja todo el estado del juego."""
        self.screen.fill(self.bg_color)

        # 1. Dibujar vecinos
        for v_id, v_data in neighbors.items():
            v_pos = v_data["pos"]
            
            # Color: Negro si no está revelado, color real si sí
            color = v_data.get("skin_color", (0, 0, 0))
            
            # Dibujar el cuerpo
            pygame.draw.circle(self.screen, color, v_pos, self.player_radius)
            
            # Si está revelado, dibujar nombre
            if v_data.get("revelado") is True:
                name_tag = self.font.render(v_data.get("nombre", "Unknown"), True, (50, 50, 50))
                self.screen.blit(name_tag, (v_pos[0] - 20, v_pos[1] - 40))
            
            # Opcional: Círculo de proximidad (ayuda visual para la demo)
            # pygame.draw.circle(self.screen, (200, 200, 200), v_pos, PROXIMITY_THRESHOLD, 1)

        # 2. Dibujar mi jugador
        pygame.draw.circle(self.screen, player.skin_color, (player.x, player.y), self.player_radius)
        pygame.draw.circle(self.screen, (0, 0, 0), (player.x, player.y), self.player_radius, 2) # Contorno

        pygame.display.flip()
