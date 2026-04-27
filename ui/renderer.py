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
            
            if v_data.get("revelado") is True:
                self._draw_character(v_pos, v_data)
                name_tag = self.font.render(v_data.get("nombre", "Unknown"), True, (50, 50, 50))
                self.screen.blit(name_tag, (v_pos[0] - 20, v_pos[1] - 60))
            else:
                # Si no está revelado, dibujar un círculo gris o negro
                pygame.draw.circle(self.screen, (150, 150, 150), v_pos, self.player_radius)

        # 2. Dibujar mi jugador
        my_data = {
            "skin_color": player.skin_color,
            "tshirt_color": player.tshirt_color,
            "pants_color": player.pants_color,
            "shoes_color": player.shoes_color,
            "glasses_type": player.glasses_type,
            "hat_type": player.hat_type
        }
        self._draw_character((player.x, player.y), my_data)

        pygame.display.flip()

    def _draw_character(self, pos, data):
        x, y = pos
        skin = data.get("skin_color", (255, 224, 189))
        tshirt = data.get("tshirt_color", (255, 0, 0))
        pants = data.get("pants_color", (0, 0, 255))
        shoes = data.get("shoes_color", (50, 50, 50))
        glasses = data.get("glasses_type")
        hat = data.get("hat_type")

        # Cuerpo (T-shirt)
        pygame.draw.rect(self.screen, tshirt, (x - 12, y - 5, 24, 20))
        # Pantalones
        pygame.draw.rect(self.screen, pants, (x - 12, y + 15, 24, 15))
        # Zapatos
        pygame.draw.rect(self.screen, shoes, (x - 12, y + 30, 10, 5))
        pygame.draw.rect(self.screen, shoes, (x + 2, y + 30, 10, 5))
        # Cabeza (Skin)
        pygame.draw.circle(self.screen, skin, (x, y - 15), 15)
        
        # Gafas
        if glasses == 'simple':
            pygame.draw.line(self.screen, (0, 0, 0), (x - 10, y - 18), (x + 10, y - 18), 2)
            pygame.draw.rect(self.screen, (0, 0, 0), (x - 10, y - 22, 8, 8), 1)
            pygame.draw.rect(self.screen, (0, 0, 0), (x + 2, y - 22, 8, 8), 1)
        elif glasses == 'sun':
            pygame.draw.rect(self.screen, (0, 0, 0), (x - 10, y - 22, 20, 8))
        
        # Sombrero
        if hat == 'cap':
            pygame.draw.rect(self.screen, (200, 0, 0), (x - 15, y - 30, 30, 10))
            pygame.draw.rect(self.screen, (200, 0, 0), (x, y - 30, 25, 5))
        elif hat == 'top':
            pygame.draw.rect(self.screen, (0, 0, 0), (x - 15, y - 30, 30, 5))
            pygame.draw.rect(self.screen, (0, 0, 0), (x - 10, y - 50, 20, 20))
