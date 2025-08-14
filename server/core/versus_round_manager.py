"""round manager class"""
from core.battle_manager import BattleManager
from entities.battle_result import BattleResult
from board.player import Player
from util import helpers


class RoundManager:
    """manages a round of a game inclusing the shop phase and the battle phase between """
    def __init__(self, player1:Player, player2:Player):
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
        self.battle_manager = BattleManager(self.player1, self.player2)
        result = self.battle_manager.battle()
        print(result)
        self.process_results(result)

    def process_results(self, result:BattleResult):
        """processes the results of the battle phase"""
        #TODO implement
def test():
    player1 = Player("p1", 1)
    player2 = Player("p2", 2)
    round_manager = RoundManager(player1, player2)

    player1.loadout[1] = helpers.create_pet_from_json("Mosquito")
    player1.loadout[2] = helpers.create_pet_from_json("Dodo")
    player1.loadout[3] = helpers.create_pet_from_json("Skunk")
    player2.loadout[1] = helpers.create_pet_from_json("Crab")
    player2.loadout[2] = helpers.create_pet_from_json("Whale")
    player2.loadout[3] = helpers.create_pet_from_json("Dolphin")
    # player2.loadout[4] = helpers.create_pet_from_json("Dolphin")
    # player2.loadout[5] = helpers.create_pet_from_json("Dolphin")
    round_manager.battle_phase()