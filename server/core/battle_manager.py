"""battle manager class"""
import copy
from server.entities.battle_result import BattleResult

class BattleManager:
    """ manages the battle between two loadouts"""

    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.battle_loadout1 = copy.deepcopy(self.player1.loadout)
        self.battle_loadout2 = copy.deepcopy(self.player2.loadout)

    def battle(self) -> BattleResult:
        """starts the battle and returns the battle result"""
        while not self.is_battle_over():
            self.attack_phase()
            self.resolve_deaths()
            self.resolve_after_death_abilities()
        return self.resolve_winner()

    def is_battle_over(self):
        """returns whether the battle is over or not"""
        if self.battle_loadout1.is_empty() or self.battle_loadout2.is_empty():
            return True
        return False

    def attack_phase(self):
        """plays the attack phase of the battle"""
        #TODO implement attack phase

    def resolve_deaths(self):
        """resolves the deaths of the battle"""
        for i, pet in enumerate(self.battle_loadout1):
            if pet is not None and pet.health <= 0:
                self.battle_loadout1[i] = None
        for i, pet in enumerate(self.battle_loadout2):
            if pet is not None and pet.health <= 0:
                self.battle_loadout2[i] = None

    def resolve_after_death_abilities(self):
        """resolves the after death abilities of the battle"""
        #TODO implement after death abilities

    def resolve_winner(self):
        """resolves the winner of the battle and returns a battle_result"""
        if self.battle_loadout1.is_empty():
            if self.battle_loadout2.is_empty():
                return BattleResult(True)
            else:
                return BattleResult(False, self.player2, self.player1)
        elif self.battle_loadout2.is_empty():
            return BattleResult(False, self.player1, self.player2)

