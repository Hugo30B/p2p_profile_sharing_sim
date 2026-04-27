import socket
import threading
import json
import time
from config import UDP_PORT, BROADCAST_IP, BIND_IP

class UDPNode:
    def __init__(self, player_ref, neighbors_dict):
        self.player = player_ref # Referencia a la instancia del usuario
        self.neighbors = neighbors_dict # Diccionario compartido {id: datos}
        self.running = True

        # Configuración del Socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        if hasattr(socket, 'SO_REUSEPORT'):
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            
        self.sock.bind((BIND_IP, UDP_PORT))
        self.sock.settimeout(0.2)

    def start(self):
        # Lanzamos emisor y receptor en hilos separados
        threading.Thread(target=self._run_emitter, daemon=True).start()
        threading.Thread(target=self._run_receiver, daemon=True).start()

    def _run_emitter(self):
        """Envía posición y puerto Pyro al resto"""
        while self.running:
            data = {
                "id": self.player.id,
                "pos": [self.player.x, self.player.y],
                "pyro_port": self.player.pyro_port,
                "nombre": self.player.nombre
            }
            msg = json.dumps(data).encode()
            self.sock.sendto(msg, (BROADCAST_IP, UDP_PORT))
            time.sleep(0.016)

    def _run_receiver(self):
        """Escucha a los vecinos"""
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                try:
                    info = json.loads(data.decode())
                except json.JSONDecodeError:
                    continue

                # Ignorarse a mí mismo
                if info["id"] == self.player.id:
                    continue
                
                # Guardar IP y datos del vecino
                info["ip"] = addr[0]
                info["last_seen"] = time.time()
                
                if info["id"] in self.neighbors:
                    self.neighbors[info["id"]].update(info) # En la clave delid que hemos encontrado, actualizamos solo lo que haya cambiado
                else:
                    # Nuevo vecino descubierto
                    self.neighbors[info["id"]] = info # Crea un nuevo diccionario dentro del ciccionario con clave "id"
            except socket.timeout:
                continue