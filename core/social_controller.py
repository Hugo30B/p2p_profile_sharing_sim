import threading
import Pyro5.api
from config import FOLLOW_DISTANCE, REACTION_DURATION
from core.social import SocialState


class SocialController:
    def __init__(self, player, neighbors):
        self.player = player
        self.neighbors = neighbors
        self.state = SocialState(player, reaction_duration=REACTION_DURATION)

    def update_from_neighbor(self, neighbor_id, neighbor_data):
        profile = self.state.update_profile_from_data(neighbor_data, neighbor_data.get("pos"))
        self.state.mark_seen(profile.id, neighbor_data.get("pos"))

    def nearest_neighbor(self):
        closest = None
        best_dist = None
        for v_id, v_data in self.neighbors.items():
            v_pos = v_data.get("pos")
            if not v_pos:
                continue
            dist = ((self.player.x - v_pos[0]) ** 2 + (self.player.y - v_pos[1]) ** 2) ** 0.5
            if dist <= FOLLOW_DISTANCE and (best_dist is None or dist < best_dist):
                closest = (v_id, v_data, dist)
                best_dist = dist
        return closest

    def nearest_friend(self):
        closest = None
        best_dist = None
        for v_id, v_data in self.neighbors.items():
            if v_id not in self.state.friends:
                continue
            v_pos = v_data.get("pos")
            if not v_pos:
                continue
            dist = ((self.player.x - v_pos[0]) ** 2 + (self.player.y - v_pos[1]) ** 2) ** 0.5
            if dist <= FOLLOW_DISTANCE and (best_dist is None or dist < best_dist):
                closest = (v_id, v_data, dist)
                best_dist = dist
        return closest

    def nearby_profiles(self, max_count=6):
        items = []
        for v_id, v_data in self.neighbors.items():
            if v_data.get("revelado") is not True:
                continue
            v_pos = v_data.get("pos")
            if not v_pos:
                continue
            dist = ((self.player.x - v_pos[0]) ** 2 + (self.player.y - v_pos[1]) ** 2) ** 0.5
            if dist <= FOLLOW_DISTANCE:
                items.append((dist, v_id))
        items.sort(key=lambda item: item[0])
        return [item[1] for item in items[:max_count]]

    def request_follow(self, neighbor_id):
        data = self.neighbors.get(neighbor_id)
        if not data:
            return
        if neighbor_id in self.state.friends or neighbor_id in self.state.pending_outgoing:
            return
        self.state.pending_outgoing.add(neighbor_id)
        threading.Thread(
            target=self._follow_thread,
            args=(neighbor_id, data),
            daemon=True,
        ).start()

    def _follow_thread(self, neighbor_id, data):
        uri = f"PYRO:social@{data['ip']}:{data['pyro_port']}"
        try:
            with Pyro5.api.Proxy(uri) as proxy:
                response = proxy.request_follow(self.state.my_profile().to_dict())
                if response and response.get("accepted"):
                    profile = response.get("profile", {})
                    self.state.handle_outgoing_follow_accept(profile)
        except Exception:
            self.state.pending_outgoing.discard(neighbor_id)

    def accept_follow(self, profile_id):
        profile = self.state.accept_follow(profile_id)
        if not profile:
            return
        data = self.neighbors.get(profile.id)
        if not data:
            return
        threading.Thread(
            target=self._follow_accept_thread,
            args=(profile, data),
            daemon=True,
        ).start()

    def _follow_accept_thread(self, profile, data):
        uri = f"PYRO:social@{data['ip']}:{data['pyro_port']}"
        try:
            with Pyro5.api.Proxy(uri) as proxy:
                proxy.confirm_follow(self.state.my_profile().to_dict())
        except Exception:
            pass

    def deny_follow(self, profile_id):
        self.state.deny_follow(profile_id)

    def send_dm(self, neighbor_id, text):
        data = self.neighbors.get(neighbor_id)
        if not data:
            return
        
        v_pos = data.get("pos")
        is_nearby = False
        if v_pos:
            dist = ((self.player.x - v_pos[0]) ** 2 + (self.player.y - v_pos[1]) ** 2) ** 0.5
            is_nearby = dist <= FOLLOW_DISTANCE

        if not (self.state.is_friend(neighbor_id) or is_nearby):
            return
            
        self.state.add_dm(neighbor_id, text, incoming=False)
        threading.Thread(
            target=self._dm_thread,
            args=(neighbor_id, data, text),
            daemon=True,
        ).start()

    def _dm_thread(self, neighbor_id, data, text):
        uri = f"PYRO:social@{data['ip']}:{data['pyro_port']}"
        try:
            with Pyro5.api.Proxy(uri) as proxy:
                proxy.send_dm(self.state.my_profile().to_dict(), text)
        except Exception:
            pass

    def send_reaction(self, neighbor_id, text):
        data = self.neighbors.get(neighbor_id)
        if not data:
            return
        self.state.add_reaction(neighbor_id, text)
        threading.Thread(
            target=self._reaction_thread,
            args=(neighbor_id, data, text),
            daemon=True,
        ).start()

    def _reaction_thread(self, neighbor_id, data, text):
        uri = f"PYRO:social@{data['ip']}:{data['pyro_port']}"
        try:
            with Pyro5.api.Proxy(uri) as proxy:
                proxy.send_reaction(self.state.my_profile().to_dict(), text)
        except Exception:
            pass

    def handle_incoming_dm(self, sender_profile, text):
        profile = self.state.update_profile_from_data(sender_profile)
        
        # Permite DM si son amigos o si están cerca (están en la lista de vecinos)
        # Como handle_incoming_dm es llamado via RPC, el sender ya debe existir en neighbors pero para ser estrictos comprobamos la distancia si no son amigos.
        if not self.state.is_friend(profile.id):
            data = self.neighbors.get(profile.id)
            if not data:
                return
            v_pos = data.get("pos")
            if not v_pos:
                return
            dist = ((self.player.x - v_pos[0]) ** 2 + (self.player.y - v_pos[1]) ** 2) ** 0.5
            if dist > FOLLOW_DISTANCE:
                return
                
        self.state.add_dm(profile.id, text, incoming=True)

    def handle_incoming_reaction(self, sender_profile, text):
        profile = self.state.update_profile_from_data(sender_profile)
        self.state.add_reaction(profile.id, text)

    def handle_incoming_follow(self, sender_profile):
        profile = self.state.update_profile_from_data(sender_profile)
        response = self.state.handle_incoming_follow_request(sender_profile)
        return response

    def handle_follow_confirm(self, sender_profile):
        profile = self.state.update_profile_from_data(sender_profile)
        self.state.handle_outgoing_follow_accept(profile.to_dict())
        self.state.pending_outgoing.discard(profile.id)

    def refresh_known_profiles(self):
        for v_id, v_data in self.neighbors.items():
            if v_data.get("revelado") is True:
                self.update_from_neighbor(v_id, v_data)
