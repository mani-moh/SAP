"""battle result class"""
from board.player import Player

class BattleResult:
    """represents the result of a battle"""
    def __init__(self, is_draw:bool, winner:Player = None, loser:Player =None, log:list = None):
        self.is_draw = is_draw
        self.winner = winner
        self.loser = loser
        self.log = log

    def __str__(self):
        log_str = "\n".join([f"{i}: {str(event)}" for i,event in enumerate(self.log)])
        result = {f"winner":f"{self.winner}", "log":f"{log_str}"}
        return str(result)