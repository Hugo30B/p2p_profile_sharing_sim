import Pyro5.api
import threading
from config import BIND_IP

@Pyro5.api.expose
class StreetPassService:
    def __init__(self, player_ref):
        self.player = player_ref # Referencia a la instancia del usuario

    def get_profile(self):
        """Este método lo llama el vecino cuando está cerca"""
        print(f"-> Alguien ha pedido mi perfil ({self.player.nombre})")
        return {
            "nombre": self.player.nombre,
            "skin_color": self.player.skin_color,
            "shoes_color": self.player.shoes_color,
            "pants_color": self.player.pants_color,
            "tshirt_color": self.player.tshirt_color,
            "glasses_type": self.player.glasses_type,
            "hat_type": self.player.hat_type,
            "mensaje": "Hola!"
        }

class PyroServer:
    def __init__(self, player_ref):
        self.player = player_ref
        # Port 0 para recibir uno libre automáticamente
        self.daemon = Pyro5.api.Daemon(host=BIND_IP, port=0)
        self.uri = self.daemon.register(StreetPassService(self.player), "streetpass")
        
        # Guardamos el puerto asignado en a instancia para que el UDP lo anuncie
        self.player.pyro_port = self.daemon.sock.getsockname()[1]

    def start(self):
        threading.Thread(target=self.daemon.requestLoop, daemon=True).start()
        print(f"Servidor Pyro listo en puerto {self.player.pyro_port}")