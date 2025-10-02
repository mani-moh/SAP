"""battle manager class"""
from __future__ import annotations
import copy
from entities.battle_result import BattleResult
from entities.loadout import Loadout
from entities.player_pet import PlayerPet
from core.event_manager import EventManager

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from board.player import Player

class BattleManager:
    """ manages the battle between two loadouts"""
    start_of_battle_classes = ("start of battle",)
    before_attack_classes = ("before attack",)
    def __init__(self, player1, player2):
        self.player1: Player = player1
        self.player2: Player = player2
        self.battle_loadout1 : Loadout = copy.deepcopy(self.player1.loadout)
        self.battle_loadout2 : Loadout = copy.deepcopy(self.player2.loadout)
        self.loadouts = [self.battle_loadout1, self.battle_loadout2]
        self.log = []
        self.event_manager = EventManager(self)
        
        for loadout in self.loadouts:
            for player_pet in loadout:
                if player_pet is not None:
                    func = player_pet.pet.ability_func
                    self.event_manager.subscribe(player_pet.pet.ability_class, func, player_pet)
                    for ability in player_pet.pet.secondary_abilities:
                        self.event_manager.subscribe(ability["ability_class"], ability["ability"], player_pet)

    def battle(self) -> BattleResult:
        """starts the battle and returns the battle result"""
        self.log.append({"type":"start battle"})
        self.event_manager.post("start of battle")
        print(f"loadout1:{self.battle_loadout1.to_dict()}")
        print(f"loadout2:{self.battle_loadout2.to_dict()}\n")
        self.resolve_deaths()
        while not self.is_battle_over():
            self.push_forward()
            print(f"loadout1:{self.battle_loadout1.to_dict()}")
            print(f"loadout2:{self.battle_loadout2.to_dict()}\n")
            self.attack_phase()
            self.resolve_deaths()
        return self.resolve_winner()

    def is_battle_over(self):
        """returns whether the battle is over or not"""
        if self.battle_loadout1.is_empty() or self.battle_loadout2.is_empty():
            return True
        return False

    def push_forward(self):
        """pushes all the pets to the front"""
        for loadout in self.loadouts:
            for i, _ in enumerate(loadout):
                i += 1
                if i > 0:
                    current_pos = i + 1
                    if current_pos < 6 and loadout[current_pos] is not None:
                        while current_pos > 1 and loadout[current_pos-1] is None:
                            loadout.swap(current_pos, current_pos - 1)
                            self.log.append({"type":"swap", "loadout":loadout.index, "pos1":current_pos, "pos2":current_pos-1})
                            current_pos -= 1

    def attack_phase(self):
        """plays the attack phase of the battle"""
        damage_amount1 = self.battle_loadout1[1].damage_amount()
        damage_amount2 = self.battle_loadout2[1].damage_amount()
        self.battle_loadout1[1].take_damage(damage_amount2)
        self.battle_loadout2[1].take_damage(damage_amount1)
        self.log.append({"type":"attack", "pet1 damaged":damage_amount2, "pet2 damaged":damage_amount1})

    def resolve_deaths(self):
        """resolves the deaths of the battle"""
        for j, loadout in enumerate(self.loadouts):
            for i, player_pet in enumerate(loadout):
                if player_pet is not None and not player_pet.alive:
                    self.log.append({"type":"faint", "loadout":j+1, "pos":i+1, "name":player_pet.pet.name})
                    self.event_manager.post("faint", player_pet=player_pet)
                    for k,p_pet in enumerate(loadout):
                        if p_pet is player_pet:
                            loadout[k+1] = None

    # def start_of_battle_abilities(self):
    #     """resolves the start of battle abilities of the battle"""
    #     # implement start of battle abilities

    # def before_attack_abilities(self):
    #     """resolves the before attack abilities of the battle"""
    #     # implement before attack abilities

    # def after_attck_abilities(self):
    #     """resolves the after attack abilities of the battle"""
    #     # implement after attack abilities

    # def faint_abilities(self):
    #     """resolves the after death abilities of the battle"""
    #     # implement after death abilities

    def resolve_winner(self):
        """resolves the winner of the battle and returns a battle_result"""
        if self.battle_loadout1.is_empty():
            if self.battle_loadout2.is_empty():
                self.log.append({"type":"battle over", "winner":"draw"})
                return BattleResult(is_draw=True, log=self.log)
            else:
                self.log.append({"type":"battle over", "winner":2})
                return BattleResult(is_draw=False, winner=self.player2, loser=self.player1, log = self.log)
        elif self.battle_loadout2.is_empty():
            self.log.append({"type":"battle over", "winner":1})
            return BattleResult(is_draw=False, winner=self.player1, loser=self.player2, log = self.log)

    def which_loadout(self, player_pet:PlayerPet) -> Loadout:
        """returns the loadout of the player pet"""
        if player_pet in self.battle_loadout1:
            return self.battle_loadout1
        elif player_pet in self.battle_loadout2:
            return self.battle_loadout2
        else:
            return None


