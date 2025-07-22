"""battle result class"""
from server.board.player import Player

class BattleResult:
    """represents the result of a battle"""
    def __init__(self, is_draw:bool, winner:Player = None, loser:Player =None):
        self.is_draw = is_draw
        self.winner = winner
        self.loser = loser
