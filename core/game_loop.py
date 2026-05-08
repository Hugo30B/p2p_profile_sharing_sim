import threading
import time
import pygame
import Pyro5.api
from config import NEIGHBOR_TIMEOUT, PROXIMITY_THRESHOLD


def intercambio(ip_vecino, puerto_vecino, neighbors_dict, target_id):
    """Llamada con Pyro5 para obtener el perfil real"""
    uri = f"PYRO:social@{ip_vecino}:{puerto_vecino}"
    try:
        with Pyro5.api.Proxy(uri) as proxy:
            perfil = proxy.get_profile()
            neighbors_dict[target_id].update({
                "skin_color": perfil["skin_color"],
                "shoes_color": perfil["shoes_color"],
                "pants_color": perfil["pants_color"],
                "tshirt_color": perfil["tshirt_color"],
                "glasses_type": perfil["glasses_type"],
                "hat_type": perfil["hat_type"],
                "nombre": perfil["nombre"],
                "bio": perfil.get("bio", ""),
                "status": perfil.get("status", ""),
                "revelado": True,
            })
            print(f"Intercambio con {perfil['nombre']} exitoso!")
    except Exception as e:
        print(f"Error en intercambio con {ip_vecino}: {e}")
        if target_id in neighbors_dict:
            neighbors_dict[target_id]["revelado"] = False


def run_game_loop(player, neighbors, renderer, social_controller, social_ui):
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_TAB:
                    social_ui.toggle_menu()
                if social_ui.current_tab == "dm" and event.key == pygame.K_RETURN:
                    text = social_ui.dm_input.strip()
                    if text:
                        social_controller.send_dm(social_ui.dm_target, text)
                        social_ui.clear_text()
                social_ui.text_input(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if social_ui.menu_open:
                        _social_click(event.pos, social_ui, social_controller)

        dx, dy = 0, 0
        if not social_ui.menu_open:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                dx = -5
            if keys[pygame.K_d]:
                dx = 5
            if keys[pygame.K_w]:
                dy = -5
            if keys[pygame.K_s]:
                dy = 5
        player.move(dx, dy, 800, 600)

        ahora = time.time()
        for v_id, v_data in list(neighbors.items()):
            if ahora - v_data.get("last_seen", 0) > NEIGHBOR_TIMEOUT:
                del neighbors[v_id]
                continue

            v_pos = v_data["pos"]
            dist = ((player.x - v_pos[0]) ** 2 + (player.y - v_pos[1]) ** 2) ** 0.5

            if dist < PROXIMITY_THRESHOLD and not v_data.get("revelado"):
                v_data["revelado"] = "proceso"
                threading.Thread(
                    target=intercambio,
                    args=(v_data["ip"], v_data["pyro_port"], neighbors, v_id),
                    daemon=True,
                ).start()

        social_controller.refresh_known_profiles()
        ui_state = social_ui.ui_state()
        renderer.render(player, neighbors, social_controller.state, ui_state)
        clock.tick(60)

    pygame.quit()


def _social_click(pos, social_ui, social_controller):
    x, y = pos
    frame = pygame.Rect(40, 40, 720, 520)
    if not frame.collidepoint(x, y):
        return

    tabs = [
        ("inicio", pygame.Rect(240, 56, 90, 30)),
        ("amigos", pygame.Rect(340, 56, 90, 30)),
        ("lista", pygame.Rect(440, 56, 90, 30)),
        ("dm", pygame.Rect(540, 56, 90, 30)),
        ("reacciones", pygame.Rect(640, 56, 90, 30)),
    ]
    for key, rect in tabs:
        if rect.collidepoint(x, y):
            social_ui.select_tab(key)
            return

    content = pygame.Rect(60, 120, 680, 430)
    tab = social_ui.current_tab
    if tab == "inicio":
        _home_click(content, pos, social_ui, social_controller)
    elif tab == "amigos":
        _friends_click(content, pos, social_ui, social_controller)
    elif tab == "lista":
        _list_click(content, pos, social_ui, social_controller)
    elif tab == "dm":
        _dm_click(content, pos, social_ui)
    elif tab == "reacciones":
        _reaction_click(content, pos, social_ui, social_controller)


def _home_click(panel, pos, social_ui, social_controller):
    x, y = pos
    pending_box = pygame.Rect(panel.x + 310, panel.y + 180, 350, 240)
    if not pending_box.collidepoint(x, y):
        return
    item_y = pending_box.y + 46
    for profile in list(social_controller.state.pending_incoming.values())[:4]:
        row = pygame.Rect(pending_box.x + 12, item_y, 200, 22)
        accept = pygame.Rect(pending_box.x + 220, item_y, 50, 22)
        deny = pygame.Rect(pending_box.x + 280, item_y, 50, 22)
        if row.collidepoint(x, y) or accept.collidepoint(x, y):
            social_controller.accept_follow(profile.id)
            return
        if deny.collidepoint(x, y):
            social_controller.deny_follow(profile.id)
            return
        item_y += 22


def _friends_click(panel, pos, social_ui, social_controller):
    x, y = pos
    list_box = pygame.Rect(panel.x + 16, panel.y + 16, 280, 398)
    if list_box.collidepoint(x, y):
        item_y = list_box.y + 44
        for friend_id in list(social_controller.state.friends)[:8]:
            row = pygame.Rect(list_box.x + 12, item_y, 200, 22)
            if row.collidepoint(x, y):
                social_ui.select_profile(friend_id)
                return
            item_y += 22

    detail_box = pygame.Rect(panel.x + 320, panel.y + 16, 340, 398)
    button = pygame.Rect(detail_box.x + 120, detail_box.y + 320, 160, 40)
    if button.collidepoint(x, y):
        if social_ui.selected_profile_id:
            target_id = social_ui.selected_profile_id
            # Verificar si es amigo o está cerca para permitir DM
            is_friend = social_controller.state.is_friend(target_id)
            is_nearby = False
            data = social_controller.neighbors.get(target_id)
            if data: # Esto es algo redundante, la distencia no se debería caluclar más de una vez en todo el código, debe estar globalizado de alguna manera de determinar si está cerca o no
                v_pos = data.get("pos")
                if v_pos:
                    dist = ((social_controller.player.x - v_pos[0]) ** 2 + (social_controller.player.y - v_pos[1]) ** 2) ** 0.5
                    if dist <= 70: # FOLLOW_DISTANCE
                        is_nearby = True
            
            if is_friend or is_nearby:
                social_ui.open_dm(target_id)
                return

    follow_btn = pygame.Rect(detail_box.x + 120, detail_box.y + 270, 160, 36)
    if follow_btn.collidepoint(x, y):
        if social_ui.selected_profile_id:
            target_id = social_ui.selected_profile_id
            if not social_controller.state.is_friend(target_id) and not social_controller.state.has_pending_outgoing(target_id):
                social_controller.request_follow(target_id)


def _list_click(panel, pos, social_ui, social_controller):
    x, y = pos
    start_x = panel.x + 12
    start_y = panel.y + 50
    for idx, profile_id in enumerate(social_controller.state.social_list[:9]):
        col = idx % 3
        row = idx // 3
        slot = pygame.Rect(start_x + col * 220, start_y + row * 130, 200, 110)
        if slot.collidepoint(x, y):
            social_ui.select_tab("amigos")
            social_ui.select_profile(profile_id)
            return


def _dm_click(panel, pos, social_ui):
    x, y = pos
    input_box = pygame.Rect(panel.x + 12, panel.y + 380, panel.width - 24, 36)
    if input_box.collidepoint(x, y):
        return


def _reaction_click(panel, pos, social_ui, social_controller):
    x, y = pos
    start_x = panel.x + 12
    start_y = panel.y + 50
    for idx, text in enumerate(social_ui.reaction_options):
        col = idx % 3
        row = idx // 3
        btn = pygame.Rect(start_x + col * 140, start_y + row * 50, 120, 36)
        if btn.collidepoint(x, y):
            target = social_controller.nearest_neighbor()
            if target:
                social_controller.send_reaction(target[0], text)
            return
