"""player class"""

from server.entities.loadout import Loadout

class Player:
    """
    Represents a player
    """
    def __init__(self, name):
        self.name = name
        self.loadout = Loadout()
