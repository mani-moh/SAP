"""battle manager class"""
import copy
from server.entities.battle_result import BattleResult
from server.entities.loadout import Loadout

class BattleManager:
    """ manages the battle between two loadouts"""

    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.battle_loadout1 : Loadout = copy.deepcopy(self.player1.loadout)
        self.battle_loadout2 : Loadout = copy.deepcopy(self.player2.loadout)
        self.loadouts = [self.battle_loadout1, self.battle_loadout2]

    def battle(self) -> BattleResult:
        """starts the battle and returns the battle result"""
        self.start_of_battle_abilities()
        while not self.is_battle_over():
            self.push_forward()
            self.before_attack_abilities()
            self.attack_phase()
            self.after_attck_abilities()
            self.resolve_deaths()
            self.faint_abilities()
        return self.resolve_winner()

    def is_battle_over(self):
        """returns whether the battle is over or not"""
        if self.battle_loadout1.is_empty() or self.battle_loadout2.is_empty():
            return True
        return False

    def push_forward(self):
        """pushes all the pets to the front"""
        for loadout in self.loadouts:
            for i, player_pet in enumerate(loadout):
                if i > 0:
                    current_pos = i + 1
                    while loadout[current_pos-1] is None:
                        loadout.swap(current_pos, current_pos - 1)

    def attack_phase(self):
        """plays the attack phase of the battle"""
        self.battle_loadout1[1].take_damage(self.battle_loadout2[1].damage_amount())
        self.battle_loadout2[1].take_damage(self.battle_loadout1[1].damage_amount())

    def resolve_deaths(self):
        """resolves the deaths of the battle"""
        for loadout in self.loadouts:
            for i, player_pet in enumerate(loadout):
                if player_pet is not None and not player_pet.alive:
                    loadout[i] = None

    def start_of_battle_abilities(self):
        """resolves the start of battle abilities of the battle"""
        #TODO implement start of battle abilities

    def before_attack_abilities(self):
        """resolves the before attack abilities of the battle"""
        #TODO implement before attack abilities

    def after_attck_abilities(self):
        """resolves the after attack abilities of the battle"""
        #TODO implement after attack abilities

    def faint_abilities(self):
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
