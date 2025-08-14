"""player class"""

from entities.loadout import Loadout
from board.shop import Shop
import config

class Player:
    """
    Represents a player
    """
    def __init__(self, name, index, lives = config.player_lives):
        self.name = name
        self.loadout = Loadout(index)
        self.shop = Shop(index)
        self.lives = lives

    def __str__(self):
        return f"name:{self.name}"