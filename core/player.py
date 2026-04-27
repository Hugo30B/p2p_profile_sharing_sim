import random
import uuid

class Player:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.nombre = f"User_{self.id[:4]}"
        self.x = random.randint(50, 750)
        self.y = random.randint(50, 550)
        self.skin_color = (255, 224, 189) # Color piel por defecto
        self.shoes_color = (50, 50, 50)
        self.pants_color = (0, 0, 255)
        self.tshirt_color = (255, 0, 0)
        self.glasses_type = None # None, 'simple', 'sun'
        self.hat_type = None # None, 'cap', 'top'
        self.pyro_port = 0 

    def move(self, dx, dy, screen_width, screen_height):
        """Mueve al jugador asegurando que no se salga de los límites de la pantalla."""
        self.x = max(20, min(screen_width - 20, self.x + dx))
        self.y = max(20, min(screen_height - 20, self.y + dy))

    def get_coords(self):
        return [self.x, self.y]
