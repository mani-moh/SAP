"""player class"""

from entities.loadout import Loadout
from board.shop import Shop
import config
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.versus_game_manager import VersusGameManager
class Player:
    """
    Represents a player
    """
    def __init__(self, name, index, game_manager, lives = config.player_lives):
        self.name = name
        self.index = index
        self.loadout = Loadout(index)
        self.shop = Shop(index, self)
        self.lives = lives
        self.game_manager:VersusGameManager = game_manager
        self.coins = config.player_coins

    def __str__(self):
        return f"name:{self.name}"