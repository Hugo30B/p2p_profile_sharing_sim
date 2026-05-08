import Pyro5.api
import threading
from config import BIND_IP

@Pyro5.api.expose
class SocialService:
    def __init__(self, player_ref, social_controller):
        self.player = player_ref # Referencia a la instancia del usuario
        self.social_controller = social_controller

    def get_profile(self):
        """Este método lo llama el vecino cuando está cerca"""
        print(f"Alguien ha pedido mi perfil ({self.player.nombre})")
        return {
            "id": self.player.id,
            "nombre": self.player.nombre,
            "skin_color": self.player.skin_color,
            "shoes_color": self.player.shoes_color,
            "pants_color": self.player.pants_color,
            "tshirt_color": self.player.tshirt_color,
            "glasses_type": self.player.glasses_type,
            "hat_type": self.player.hat_type,
            "bio": self.player.bio,
            "status": self.player.status,
            "mensaje": "Hola!"
        }

    def request_follow(self, requester_profile):
        """Solicitud de seguimiento"""
        return self.social_controller.incoming_follow(requester_profile)

    def confirm_follow(self, sender_profile):
        """Confirma una solicitud aceptada."""
        self.social_controller.follow_confirm(sender_profile)
        return {"accepted": True}

    def send_dm(self, sender_profile, text):
        """Recibe DM"""
        self.social_controller.incoming_dm(sender_profile, text)
        return {"delivered": True}

    def send_reaction(self, sender_profile, text):
        """Recibe reaccion para mostrar en bocadillo."""
        self.social_controller.incoming_reaction(sender_profile, text)
        return {"delivered": True}

class PyroServer:
    def __init__(self, player_ref, social_controller):
        self.player = player_ref
        # Port 0 para recibir uno libre automáticamente
        self.daemon = Pyro5.api.Daemon(host=BIND_IP, port=0)
        self.uri = self.daemon.register(SocialService(self.player, social_controller), "social")
        
        # Guardamos el puerto asignado en a instancia para que el UDP lo anuncie
        self.player.pyro_port = self.daemon.sock.getsockname()[1]

    def start(self):
        threading.Thread(target=self.daemon.requestLoop, daemon=True).start()
        print(f"Servidor Pyro listo en puerto {self.player.pyro_port}")
