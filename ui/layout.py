import pygame


class LayoutManager:
    """Responsable de decidir qué elementos existen y sus rects/posiciones.

    Esta clase no dibuja; sólo calcula posiciones, tabs, y datos que el renderer
    puede consumir para pintar. Mantener la lógica de "qué" y "dónde" aquí
    facilita pruebas y cambios sin tocar el código de render.
    """

    def __init__(self, screen_rect: pygame.Rect):
        self.screen_rect = screen_rect

    def hud_panel_rect(self):
        return pygame.Rect(16, 16, 260, 90)

    def social_frame_rect(self):
        # Frame principal cuando el menu social está abierto
        return pygame.Rect(40, 40, 720, 520)

    def social_content_rect(self, frame_rect: pygame.Rect):
        return pygame.Rect(frame_rect.x + 20, frame_rect.y + 80, 680, 430)

    def tabs_for_social(self):
        return [
            ("inicio", "Inicio"),
            ("amigos", "Amigos"),
            ("lista", "Lista"),
            ("dm", "DM"),
            ("reacciones", "Reacciones"),
        ]

    def profile_card_rect(self, x, y):
        return pygame.Rect(x, y, 260, 320)

    def friends_left_rect(self, panel_rect: pygame.Rect):
        return pygame.Rect(panel_rect.x + 16, panel_rect.y + 16, 280, 398)

    def friends_detail_rect(self, panel_rect: pygame.Rect):
        return pygame.Rect(panel_rect.x + 320, panel_rect.y + 16, 340, 398)

    def social_list_slot(self, panel_rect: pygame.Rect, idx: int):
        # calcula la posición del slot n-th en la lista social (grid 3xN)
        col = idx % 3
        row = idx // 3
        x = panel_rect.x + 12 + col * 220
        y = panel_rect.y + 50 + row * 130
        return pygame.Rect(x, y, 200, 110)

    # Otras utilidades de layout que no deben contener lógica de negocio
    def dm_input_rect(self, panel_rect: pygame.Rect):
        return pygame.Rect(panel_rect.x + 12, panel_rect.y + 380, panel_rect.width - 24, 36)

    def nearby_box_rect(self, panel_rect: pygame.Rect):
        return pygame.Rect(panel_rect.x + 20, panel_rect.y + 360, 260, 60)

    def pending_box_rect(self, panel_rect: pygame.Rect):
        return pygame.Rect(panel_rect.x + 310, panel_rect.y + 180, 350, 240)
