from dataclasses import dataclass
import random
import uuid
import time

@dataclass
class DMMessage:
    text: str
    incoming: bool
    created_at: float


@dataclass
class ReactionBubble:
    text: str
    expires_at: float


class Player:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.nombre = f"User_{self.id[:4]}"
        self.x = random.randint(50, 750)
        self.y = random.randint(50, 550)
        self.bio = "Hola!"
        self.status = "Disponible"
        self.skin_color = random.choice([(255, 224, 189), (79, 41, 3)]) # Color piel por defecto
        self.shoes_color = (50, 50, 50)
        self.pants_color = (0, 0, 255)
        self.tshirt_color = (255, 0, 0)
        self.glasses_type = None # None, 'simple', 'sun'
        self.hat_type = None # None, 'cap', 'top'
        self.pyro_port = 0
        self.last_seen = 0.0

        # Atributos sociales (antes en SocialState)
        self.reaction_duration = 3.5
        self.known_profiles = {}
        self.social_list = []
        self.friends = set()
        self.followers = set()
        self.following = set()
        self.pending_outgoing = set()
        self.pending_incoming = {}
        self.dm_threads = {}
        self.reactions = {}

    def move(self, dx, dy, screen_width, screen_height):
        """Mueve al jugador asegurando que no se salga de los límites de la pantalla."""
        self.x = max(20, min(screen_width - 20, self.x + dx))
        self.y = max(20, min(screen_height - 20, self.y + dy))

    def get_coords(self):
        return [self.x, self.y]

    @property
    def location(self):
        return (self.x, self.y)

    @location.setter
    def location(self, value):
        self.x, self.y = value

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "skin_color": self.skin_color,
            "shoes_color": self.shoes_color,
            "pants_color": self.pants_color,
            "tshirt_color": self.tshirt_color,
            "glasses_type": self.glasses_type,
            "hat_type": self.hat_type,
            "bio": self.bio,
            "status": self.status,
            "location": (self.x, self.y),
        }

    @classmethod
    def from_dict(cls, data):
        p = cls()
        p.id = data.get("id", p.id)
        p.nombre = data.get("nombre", "Unknown")
        p.skin_color = tuple(data.get("skin_color", (255, 224, 189)))
        p.shoes_color = tuple(data.get("shoes_color", (50, 50, 50)))
        p.pants_color = tuple(data.get("pants_color", (0, 0, 255)))
        p.tshirt_color = tuple(data.get("tshirt_color", (255, 0, 0)))
        p.glasses_type = data.get("glasses_type")
        p.hat_type = data.get("hat_type")
        p.bio = data.get("bio", "")
        p.status = data.get("status", "")
        loc = data.get("location") or data.get("pos") or (0, 0)
        p.x, p.y = loc
        return p

    # Métodos sociales
    def update_profile_from_data(self, data, position=None):
        profile = Player.from_dict(data)
        if position is not None:
            profile.x, profile.y = position
        self.known_profiles[profile.id] = profile
        if profile.id not in self.social_list:
            self.social_list.append(profile.id)
        return profile

    def mark_seen(self, profile_id, position=None):
        profile = self.known_profiles.get(profile_id)
        if profile:
            profile.last_seen = time.time()
            if position is not None:
                profile.x, profile.y = position

    def is_friend(self, profile_id):
        return profile_id in self.friends

    def has_pending_outgoing(self, profile_id):
        return profile_id in self.pending_outgoing

    def add_friend(self, profile_id):
        self.friends.add(profile_id)
        self.following.add(profile_id)
        self.followers.add(profile_id)

    def incoming_follow_request(self, requester_profile):
        profile = self.update_profile_from_data(requester_profile)
        self.pending_incoming[profile.id] = profile
        return {
            "accepted": False,
            "profile": self.to_dict(),
        }

    def outgoing_follow_accept(self, target_profile_dict):
        profile = self.update_profile_from_data(target_profile_dict)
        self.pending_outgoing.discard(profile.id)
        self.add_friend(profile.id)

    def accept_follow(self, profile_id):
        profile = self.pending_incoming.pop(profile_id, None)
        if not profile:
            return None
        self.add_friend(profile.id)
        return profile

    def deny_follow(self, profile_id):
        if profile_id in self.pending_incoming:
            del self.pending_incoming[profile_id]

    def can_message(self, profile_id):
        return profile_id in self.friends

    def add_dm(self, profile_id, text, incoming):
        thread = self.dm_threads.setdefault(profile_id, [])
        thread.append(DMMessage(text=text, incoming=incoming, created_at=time.time()))

    def add_reaction(self, profile_id, text):
        self.reactions[profile_id] = ReactionBubble(
            text=text,
            expires_at=time.time() + self.reaction_duration,
        )

    def get_active_reaction(self, profile_id):
        bubble = self.reactions.get(profile_id)
        if not bubble:
            return None
        if time.time() > bubble.expires_at:
            del self.reactions[profile_id]
            return None
        return bubble.text
