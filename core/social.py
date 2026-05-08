from dataclasses import dataclass
import time


@dataclass
class SocialProfile:
    id: str
    nombre: str
    skin_color: tuple
    shoes_color: tuple
    pants_color: tuple
    tshirt_color: tuple
    glasses_type: str | None
    hat_type: str | None
    bio: str
    status: str
    last_seen: float = 0.0
    location: tuple = (0, 0)

    @classmethod
    def from_player(cls, player):
        return cls(
            id=player.id,
            nombre=player.nombre,
            skin_color=player.skin_color,
            shoes_color=player.shoes_color,
            pants_color=player.pants_color,
            tshirt_color=player.tshirt_color,
            glasses_type=player.glasses_type,
            hat_type=player.hat_type,
            bio=player.bio,
            status=player.status,
            location=(player.x, player.y),
            last_seen=time.time(),
        )

    @classmethod
    def from_data(cls, data):
        return cls(
            id=data.get("id"),
            nombre=data.get("nombre", "Unknown"),
            skin_color=tuple(data.get("skin_color", (255, 224, 189))),
            shoes_color=tuple(data.get("shoes_color", (50, 50, 50))),
            pants_color=tuple(data.get("pants_color", (0, 0, 255))),
            tshirt_color=tuple(data.get("tshirt_color", (255, 0, 0))),
            glasses_type=data.get("glasses_type"),
            hat_type=data.get("hat_type"),
            bio=data.get("bio", ""),
            status=data.get("status", ""),
            location=tuple(data.get("location", (0, 0))),
            last_seen=time.time(),
        )

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
            "location": self.location,
        }


@dataclass
class DMMessage:
    text: str
    incoming: bool
    created_at: float


@dataclass
class ReactionBubble:
    text: str
    expires_at: float


class SocialState:
    def __init__(self, player, reaction_duration=3.5):
        self.player = player
        self.reaction_duration = reaction_duration
        self.known_profiles = {}
        self.social_list = []
        self.friends = set()
        self.followers = set()
        self.following = set()
        self.pending_outgoing = set()
        self.pending_incoming = {}
        self.dm_threads = {}
        self.reactions = {}

    def my_profile(self):
        return SocialProfile.from_player(self.player)

    def update_profile_from_data(self, data, position=None):
        profile = SocialProfile.from_data(data)
        if position is not None:
            profile.location = position
        self.known_profiles[profile.id] = profile
        if profile.id not in self.social_list:
            self.social_list.append(profile.id)
        return profile

    def mark_seen(self, profile_id, position=None):
        profile = self.known_profiles.get(profile_id)
        if profile:
            profile.last_seen = time.time()
            if position is not None:
                profile.location = position

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
            "profile": self.my_profile().to_dict(),
        }

    def outgoing_follow_accept(self, target_profile):
        profile = self.update_profile_from_data(target_profile)
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
