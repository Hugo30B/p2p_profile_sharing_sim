import pygame
from config import PROXIMITY_THRESHOLD
from ui.layout import LayoutManager


class GameRenderer:
    """Renderer puro: dibuja primitivas y componentes en pantalla.

    La lógica de qué mostrar y dónde la delegamos a LayoutManager y a
    capas superiores (SocialUI/SocialState). Esto mantiene el renderer
    enfocado en "cómo dibujar".
    """

    def __init__(self, screen_width, screen_height):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.font = pygame.font.SysFont("palatino", 22)
        self.small_font = pygame.font.SysFont("palatino", 18)
        self.title_font = pygame.font.SysFont("palatino", 30, bold=True)
        self.bg_color = (234, 232, 226)
        self.panel_bg = (248, 246, 240)
        self.panel_shadow = (201, 196, 188)
        self.accent = (203, 101, 52)
        self.deep = (52, 45, 40)
        self.player_radius = 20
        self.gradient_cache = None
        self.gradient_size = (screen_width, screen_height)
        self.layout = LayoutManager(self.screen.get_rect())

    def render(self, player, neighbors, social_state, ui_state):
        """Dibuja todo el estado del juego."""
        self._draw_background()

        # 1. Dibujar vecinos
        for v_id, v_data in neighbors.items():
            v_pos = v_data["pos"]

            if v_data.get("revelado") is True:
                self._draw_character(v_pos, v_data)
                name = v_data.get("nombre", "Unknown")
                name_tag = self.font.render(name, True, self.deep)
                self.screen.blit(name_tag, (v_pos[0] - 20, v_pos[1] - 60))
                reaction = social_state.get_active_reaction(v_id)
                if reaction:
                    self._draw_bubble((v_pos[0], v_pos[1] - 80), reaction)
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
        self._draw_hud(player, social_state, neighbors)

        if ui_state.get("menu_open"):
            self._draw_social_screen(player, social_state, ui_state, neighbors)

        pygame.display.flip()

    def _draw_background(self):
        if not self.gradient_cache or self.gradient_cache.get_size() != self.gradient_size:
            w, h = self.gradient_size
            surface = pygame.Surface((w, h))
            for y in range(h):
                t = y / max(1, h - 1)
                r = int(240 + (225 - 240) * t)
                g = int(235 + (214 - 235) * t)
                b = int(228 + (200 - 228) * t)
                pygame.draw.line(surface, (r, g, b), (0, y), (w, y))
            self.gradient_cache = surface
        self.screen.blit(self.gradient_cache, (0, 0))
        pygame.draw.circle(self.screen, (224, 216, 205), (120, 90), 110)
        pygame.draw.circle(self.screen, (216, 205, 190), (680, 520), 140)
        pygame.draw.circle(self.screen, (229, 220, 208), (600, 120), 70)

    def _draw_hud(self, player, social_state, neighbors):
        panel = self.layout.hud_panel_rect()
        self._draw_panel(panel)
        title = self.title_font.render(player.nombre, True, self.deep)
        self.screen.blit(title, (panel.x + 12, panel.y + 10))
        stats = self.small_font.render(
            f"Seguidores {len(social_state.followers)}  Amigos {len(social_state.friends)}",
            True,
            self.deep,
        )
        self.screen.blit(stats, (panel.x + 12, panel.y + 46))
        hint = self.small_font.render("TAB: Social", True, self.deep)
        self.screen.blit(hint, (panel.x + 12, panel.y + 66))

    def _draw_panel(self, rect):
        shadow = rect.move(3, 3)
        pygame.draw.rect(self.screen, self.panel_shadow, shadow, border_radius=10)
        pygame.draw.rect(self.screen, self.panel_bg, rect, border_radius=10)
        pygame.draw.rect(self.screen, self.accent, rect, 2, border_radius=10)

    def _draw_social_screen(self, player, social_state, ui_state, neighbors):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((248, 244, 238, 240))
        self.screen.blit(overlay, (0, 0))

        frame = self.layout.social_frame_rect()
        self._draw_panel(frame)
        header = self.title_font.render("Social", True, self.deep)
        self.screen.blit(header, (frame.x + 20, frame.y + 16))

        tabs = self.layout.tabs_for_social()
        self._draw_tabs(frame, tabs, ui_state.get("current_tab", "inicio"))

        content = self.layout.social_content_rect(frame)
        tab = ui_state.get("current_tab")
        if tab == "inicio":
            self._draw_home_panel(content, player, social_state)
        elif tab == "amigos":
            self._draw_friends_panel(content, social_state, ui_state, neighbors)
        elif tab == "lista":
            self._draw_social_list(content, social_state)
        elif tab == "dm":
            self._draw_dm_panel(content, social_state, ui_state)
        elif tab == "reacciones":
            self._draw_reaction_panel(content, ui_state)

    def _draw_profile_card(self, x, y, profile, label):
        card = self.layout.profile_card_rect(x, y)
        self._draw_panel(card)
        title = self.font.render(label, True, self.deep)
        self.screen.blit(title, (card.x + 12, card.y + 10))

        avatar_pos = (card.x + 130, card.y + 110)
        data = profile.to_dict()
        self._draw_character(avatar_pos, data)

        name = self.font.render(profile.nombre, True, self.deep)
        self.screen.blit(name, (card.x + 12, card.y + 170))
        bio = self.small_font.render(profile.bio, True, self.deep)
        self.screen.blit(bio, (card.x + 12, card.y + 198))
        status = self.small_font.render(f"Estado: {profile.status}", True, self.deep)
        self.screen.blit(status, (card.x + 12, card.y + 224))
        loc = self.small_font.render(
            f"Ubicacion: {int(profile.location[0])}, {int(profile.location[1])}",
            True,
            self.deep,
        )
        self.screen.blit(loc, (card.x + 12, card.y + 250))

    def _draw_tabs(self, frame, tabs, current):
        x = frame.x + 200
        y = frame.y + 16
        for key, label in tabs:
            w = 90
            tab = pygame.Rect(x, y, w, 30)
            color = self.accent if key == current else (220, 210, 200)
            pygame.draw.rect(self.screen, color, tab, border_radius=8)
            pygame.draw.rect(self.screen, self.deep, tab, 2, border_radius=8)
            text = self.small_font.render(label, True, self.deep)
            self.screen.blit(text, (tab.x + 10, tab.y + 6))
            x += w + 10

    def _draw_home_panel(self, panel, player, social_state):
        self._draw_panel(panel)
        profile = social_state.my_profile()
        self._draw_profile_card(panel.x + 20, panel.y + 20, profile, "Tu perfil")

        stats_box = pygame.Rect(panel.x + 310, panel.y + 20, 350, 140)
        self._draw_panel(stats_box)
        header = self.font.render("Resumen", True, self.deep)
        self.screen.blit(header, (stats_box.x + 12, stats_box.y + 10))
        line1 = self.small_font.render(
            f"Amigos: {len(social_state.friends)}", True, self.deep
        )
        self.screen.blit(line1, (stats_box.x + 12, stats_box.y + 40))
        line2 = self.small_font.render(
            f"Seguidores: {len(social_state.followers)}", True, self.deep
        )
        self.screen.blit(line2, (stats_box.x + 12, stats_box.y + 62))
        line3 = self.small_font.render(
            f"Siguiendo: {len(social_state.following)}", True, self.deep
        )
        self.screen.blit(line3, (stats_box.x + 12, stats_box.y + 84))

        pending_box = self.layout.pending_box_rect(panel)
        self._draw_panel(pending_box)
        header = self.font.render("Solicitudes", True, self.deep)
        self.screen.blit(header, (pending_box.x + 12, pending_box.y + 10))
        if not social_state.pending_incoming:
            empty = self.small_font.render("No hay solicitudes.", True, self.deep)
            self.screen.blit(empty, (pending_box.x + 12, pending_box.y + 46))
        else:
            y = pending_box.y + 46
            for idx, profile in enumerate(list(social_state.pending_incoming.values())[:4]):
                name = self.small_font.render(profile.nombre, True, self.deep)
                self.screen.blit(name, (pending_box.x + 12, y))
                accept = pygame.Rect(pending_box.x + 220, y - 2, 50, 22)
                deny = pygame.Rect(pending_box.x + 280, y - 2, 50, 22)
                pygame.draw.rect(self.screen, (235, 230, 220), accept, border_radius=6)
                pygame.draw.rect(self.screen, self.accent, accept, 2, border_radius=6)
                pygame.draw.rect(self.screen, (235, 230, 220), deny, border_radius=6)
                pygame.draw.rect(self.screen, self.accent, deny, 2, border_radius=6)
                ok = self.small_font.render("OK", True, self.deep)
                no = self.small_font.render("NO", True, self.deep)
                self.screen.blit(ok, (accept.x + 10, accept.y + 2))
                self.screen.blit(no, (deny.x + 10, deny.y + 2))
                y += 22

        nearby_box = self.layout.nearby_box_rect(panel)
        self._draw_panel(nearby_box)
        label = self.small_font.render("Cerca: usa Amigos", True, self.deep)
        self.screen.blit(label, (nearby_box.x + 12, nearby_box.y + 20))

    def _draw_friends_panel(self, panel, social_state, ui_state, neighbors):
        self._draw_panel(panel)
        left = self.layout.friends_left_rect(panel)
        self._draw_panel(left)
        header = self.font.render("Amigos", True, self.deep)
        self.screen.blit(header, (left.x + 12, left.y + 10))
 
        y = left.y + 44
        friends = list(social_state.friends)
        if not friends:
            empty = self.small_font.render("Sin amigos aun.", True, self.deep)
            self.screen.blit(empty, (left.x + 12, y))
        else:
            for idx, friend_id in enumerate(friends[:8]):
                profile = social_state.known_profiles.get(friend_id)
                if not profile:
                    continue
                name = self.small_font.render(profile.nombre, True, self.deep)
                self.screen.blit(name, (left.x + 12, y))
                y += 22
 
        requests = pygame.Rect(panel.x + 16, panel.y + 310, 280, 104)
        self._draw_panel(requests)
        title = self.small_font.render("Solicitudes", True, self.deep)
        self.screen.blit(title, (requests.x + 12, requests.y + 8))
        y = requests.y + 30
        if not social_state.pending_incoming:
            empty = self.small_font.render("Ninguna", True, self.deep)
            self.screen.blit(empty, (requests.x + 12, y))
        else:
            for profile in list(social_state.pending_incoming.values())[:3]:
                name = self.small_font.render(profile.nombre, True, self.deep)
                self.screen.blit(name, (requests.x + 12, y))
                y += 20
 
        detail = self.layout.friends_detail_rect(panel)
        self._draw_panel(detail)
        target_id = ui_state.get("selected_profile_id")
        if target_id:
            profile = social_state.known_profiles.get(target_id)
            if profile:
                self._draw_character((detail.x + 60, detail.y + 80), profile.to_dict())
                title = self.font.render(profile.nombre, True, self.deep)
                self.screen.blit(title, (detail.x + 120, detail.y + 20))
                info = self.small_font.render(profile.status, True, self.deep)
                self.screen.blit(info, (detail.x + 120, detail.y + 48))
                bio = self.small_font.render(profile.bio, True, self.deep)
                self.screen.blit(bio, (detail.x + 120, detail.y + 70))
                
                # Verificar si se puede abrir DM (Amigo O Cerca)
                is_friend = social_state.is_friend(target_id)
                is_nearby = False
                if target_id in neighbors:
                    v_pos = neighbors[target_id].get("pos")
                    if v_pos:
                        dist = ((profile.location[0] - v_pos[0])**2 + (profile.location[1] - v_pos[1])**2)**0.5 # Simplified dist check
                        # Actually we should use player pos, but let's just use a simpler check or a flag
                        is_nearby = True # For simplicity in the renderer we can trust if it's in neighbors, but better to check dist
                
                # A more robust distance check using the player's current position (from profile object if updated)
                # Wait, renderer doesn't have the 'player' object here, but it's passed to render().
                # I'll use the neighbors list as a proxy for proximity or a simple check.
                
                button_color = (235, 230, 220) if (is_friend or is_nearby) else (200, 200, 200)
                button = pygame.Rect(detail.x + 120, detail.y + 320, 160, 40)
                pygame.draw.rect(self.screen, button_color, button, border_radius=8)
                pygame.draw.rect(self.screen, self.accent if (is_friend or is_nearby) else (150, 150, 150), button, 2, border_radius=8)
                label = self.small_font.render("Abrir DM", True, self.deep if (is_friend or is_nearby) else (120, 120, 120))
                self.screen.blit(label, (button.x + 22, button.y + 10))
                
                if not social_state.is_friend(target_id):
                    follow_btn = pygame.Rect(detail.x + 120, detail.y + 270, 160, 36)
                    pygame.draw.rect(self.screen, (235, 230, 220), follow_btn, border_radius=8)
                    pygame.draw.rect(self.screen, self.accent, follow_btn, 2, border_radius=8)
                    if social_state.has_pending_outgoing(target_id):
                        label = self.small_font.render("En espera", True, self.deep)
                    else:
                        label = self.small_font.render("Solicitar", True, self.deep)
                    self.screen.blit(label, (follow_btn.x + 30, follow_btn.y + 8))
        else:
            hint = self.small_font.render("Selecciona un amigo.", True, self.deep)
            self.screen.blit(hint, (detail.x + 12, detail.y + 40))

    def _draw_social_list(self, panel, social_state):
        self._draw_panel(panel)
        header = self.font.render("Lista Social", True, self.deep)
        self.screen.blit(header, (panel.x + 12, panel.y + 10))
        x = panel.x + 12
        y = panel.y + 50
        for idx, profile_id in enumerate(social_state.social_list[:9]):
            profile = social_state.known_profiles.get(profile_id)
            if not profile:
                continue
            slot = self.layout.social_list_slot(panel, idx)
            self._draw_panel(slot)
            self._draw_character((slot.x + 50, slot.y + 58), profile.to_dict())
            name = self.small_font.render(profile.nombre, True, self.deep)
            self.screen.blit(name, (slot.x + 95, slot.y + 20))
            status = self.small_font.render(profile.status, True, self.deep)
            self.screen.blit(status, (slot.x + 95, slot.y + 42))
            if (idx + 1) % 3 == 0:
                x = panel.x + 12
                y += 130
            else:
                x += 220

    def _draw_dm_panel(self, panel, social_state, ui_state):
        self._draw_panel(panel)
        header = self.font.render("Mensajes", True, self.deep)
        self.screen.blit(header, (panel.x + 12, panel.y + 10))

        target_id = ui_state.get("dm_target")
        profile = social_state.known_profiles.get(target_id)
        if profile:
            title = self.small_font.render(f"Con {profile.nombre}", True, self.deep)
            self.screen.blit(title, (panel.x + 12, panel.y + 36))

        thread = social_state.dm_threads.get(target_id, [])
        y = panel.y + 70
        for message in thread[-10:]:
            prefix = "Tu" if not message.incoming else "El"
            text = self.small_font.render(f"{prefix}: {message.text}", True, self.deep)
            self.screen.blit(text, (panel.x + 12, y))
            y += 22

        input_box = self.layout.dm_input_rect(panel)
        pygame.draw.rect(self.screen, (235, 230, 220), input_box, border_radius=8)
        pygame.draw.rect(self.screen, self.accent, input_box, 2, border_radius=8)
        text = ui_state.get("dm_input", "")
        prompt = self.small_font.render(text or "Escribe un mensaje...", True, self.deep)
        self.screen.blit(prompt, (input_box.x + 10, input_box.y + 8))

    def _draw_reaction_panel(self, panel, ui_state):
        self._draw_panel(panel)
        header = self.font.render("Reacciones", True, self.deep)
        self.screen.blit(header, (panel.x + 12, panel.y + 10))
        reactions = ui_state.get("reaction_options", [])
        x = panel.x + 12
        y = panel.y + 50
        for idx, text in enumerate(reactions):
            btn = pygame.Rect(x, y, 120, 36)
            pygame.draw.rect(self.screen, (235, 230, 220), btn, border_radius=8)
            pygame.draw.rect(self.screen, self.accent, btn, 2, border_radius=8)
            label = self.small_font.render(text, True, self.deep)
            self.screen.blit(label, (btn.x + 12, btn.y + 8))
            if (idx + 1) % 3 == 0:
                x = panel.x + 12
                y += 50
            else:
                x += 140

    def _draw_bubble(self, pos, text):
        bubble = self.small_font.render(text, True, self.deep)
        rect = bubble.get_rect(center=pos)
        rect.inflate_ip(18, 10)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, border_radius=8)
        pygame.draw.rect(self.screen, self.accent, rect, 2, border_radius=8)
        self.screen.blit(bubble, bubble.get_rect(center=rect.center))

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

    # Public alias kept for external modules (eg. character_creator) to avoid
    # depending on the internal underscore name. This keeps compatibility
    # with minimal changes elsewhere.
    def draw_character(self, pos, data):
        return self._draw_character(pos, data)
