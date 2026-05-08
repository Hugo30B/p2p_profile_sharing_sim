import pygame
import sys

class CharacterCreator:
    def __init__(self, renderer):
        self.renderer = renderer
        self.font = pygame.font.SysFont("palatino", 30)
        self.small_font = pygame.font.SysFont("palatino", 22)
        # Paleta de colores extendida
        self.colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255),
            (50, 50, 50), (255, 255, 255), (255, 224, 189), (139, 69, 19), (255, 140, 0), (75, 0, 130),
            (34, 139, 34), (70, 130, 180), (255, 192, 203), (128, 128, 128), (0, 0, 0), (245, 245, 220)
        ]
        self.glasses_options = [None, 'simple', 'sun']
        self.hat_options = [None, 'cap', 'top']
        self.selected_part = "tshirt" # tshirt, pants, shoes, skin, glasses, hat

    def run(self, player):
        """Ejecuta la interfaz de creación de personaje."""
        running_setup = True
        
        while running_setup:
            self.renderer.screen.fill((200, 200, 200))
            
            # Dibujar instrucciones
            instr = self.font.render("Personaliza tu personaje. ENTER para empezar.", True, (40, 35, 30))
            self.renderer.screen.blit(instr, (50, 20))
            
            part_text = self.font.render(f"Editando: {self.selected_part.upper()}", True, (40, 35, 30))
            self.renderer.screen.blit(part_text, (50, 60))
            
            hint_text = self.small_font.render("Teclas 1-6 para elegir parte. ESPACIO para cambiar tipo (gafas/gorro).", True, (70, 60, 54))
            self.renderer.screen.blit(hint_text, (50, 85))

            # Dibujar opciones de color (en dos filas)
            for i, color in enumerate(self.colors):
                row = i // 9
                col = i % 9
                rect = pygame.Rect(50 + col*40, 120 + row*40, 30, 30)
                pygame.draw.rect(self.renderer.screen, color, rect)
                pygame.draw.rect(self.renderer.screen, (0,0,0), rect, 1)

            # Mostrar estado actual de accesorios si están seleccionados
            if self.selected_part == "glasses":
                val = str(player.glasses_type)
                info = self.font.render(f"Tipo actual: {val} (Pulsa ESPACIO)", True, (0, 0, 200))
                self.renderer.screen.blit(info, (50, 210))
            elif self.selected_part == "hat":
                val = str(player.hat_type)
                info = self.font.render(f"Tipo actual: {val} (Pulsa ESPACIO)", True, (0, 0, 200))
                self.renderer.screen.blit(info, (50, 210))

            # Previsualización
            preview_pos = (550, 300)
            player_data = {
                "skin_color": player.skin_color,
                "tshirt_color": player.tshirt_color,
                "pants_color": player.pants_color,
                "shoes_color": player.shoes_color,
                "glasses_type": player.glasses_type,
                "hat_type": player.hat_type
            }
            # Dibujamos un fondo blanco para la previsualización
            pygame.draw.rect(self.renderer.screen, (255, 255, 255), (450, 150, 200, 300))
            pygame.draw.rect(self.renderer.screen, (0, 0, 0), (450, 150, 200, 300), 2)
            self.renderer.draw_character(preview_pos, player_data)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        running_setup = False
                    elif event.key == pygame.K_1: self.selected_part = "tshirt"
                    elif event.key == pygame.K_2: self.selected_part = "pants"
                    elif event.key == pygame.K_3: self.selected_part = "shoes"
                    elif event.key == pygame.K_4: self.selected_part = "skin"
                    elif event.key == pygame.K_5: self.selected_part = "glasses"
                    elif event.key == pygame.K_6: self.selected_part = "hat"
                    
                    elif event.key == pygame.K_SPACE:
                        if self.selected_part == "glasses":
                            idx = self.glasses_options.index(player.glasses_type)
                            player.glasses_type = self.glasses_options[(idx + 1) % len(self.glasses_options)]
                        elif self.selected_part == "hat":
                            idx = self.hat_options.index(player.hat_type)
                            player.hat_type = self.hat_options[(idx + 1) % len(self.hat_options)]

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    # Detectar clic en la paleta de colores
                    for i, color in enumerate(self.colors):
                        row = i // 9
                        col = i % 9
                        rect = pygame.Rect(50 + col*40, 120 + row*40, 30, 30)
                        if rect.collidepoint(mx, my):
                            if self.selected_part == "tshirt": player.tshirt_color = color
                            elif self.selected_part == "pants": player.pants_color = color
                            elif self.selected_part == "shoes": player.shoes_color = color
                            elif self.selected_part == "skin": player.skin_color = color
