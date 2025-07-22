"""round manager class"""
from server.core.battle_manager import BattleManager
from server.entities.battle_result import BattleResult

class RoundManager:
    """manages a round of a game inclusing the shop phase and the battle phase between """
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2

    def play_round(self):
        """plays a round of the game"""
        self.shop_phase()
        self.battle_phase()

    def shop_phase(self):
        """plays the shop phase of the game"""
        self.player1.shop.reroll()
        self.player2.shop.reroll()
        #TODO implement shop phase

    def battle_phase(self):
        """plays the battle phase of the game"""
        battle_manager = BattleManager(self.player1.loadout, self.player2.loadout)
        result = battle_manager.battle()
        self.process_results(result)

    def process_results(self, result:BattleResult):
        """processes the results of the battle phase"""
        #TODO implement