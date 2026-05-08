import pygame
from config import REACTION_TEXTS


class SocialUI:
    def __init__(self, player):
        self.player = player
        self.menu_open = False
        self.dm_target = None
        self.dm_input = ""
        self.reaction_options = list(REACTION_TEXTS)
        self.selected_profile_id = None
        self.current_tab = "inicio"

    def ui_state(self):
        return {
            "menu_open": self.menu_open,
            "dm_target": self.dm_target,
            "dm_input": self.dm_input,
            "reaction_options": self.reaction_options,
            "selected_profile_id": self.selected_profile_id,
            "current_tab": self.current_tab,
        }

    def toggle_menu(self):
        self.menu_open = not self.menu_open
        if not self.menu_open:
            self.current_tab = "inicio"
            self.dm_target = None
            self.dm_input = ""
            self.selected_profile_id = None

    def open_dm(self, target_id):
        self.menu_open = True
        self.current_tab = "dm"
        self.dm_target = target_id
        self.dm_input = ""
        self.selected_profile_id = target_id

    def select_tab(self, tab_key):
        self.current_tab = tab_key
        if tab_key != "dm":
            self.dm_target = None
            self.dm_input = ""

    def select_profile(self, profile_id):
        self.selected_profile_id = profile_id

    def text_input(self, event):
        if self.current_tab != "dm":
            return
        if event.key == pygame.K_BACKSPACE:
            self.dm_input = self.dm_input[:-1]
        elif event.key == pygame.K_RETURN:
            return
        else:
            if len(event.unicode) == 1 and len(self.dm_input) < 40:
                self.dm_input += event.unicode

    def clear_text(self):
        self.dm_input = ""
