"""battle effect info class"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.battle_manager import BattleManager
    from core.versus_game_manager import VersusGameManager
    from entities.loadout import Loadout
    from entities.player_pet import PlayerPet
    from core.client import Client

class BattleEffectInfo:
    """stores information about a battle effect"""
    def __init__(self, battle_manager:BattleManager, pet_loadout:Loadout, effect_pet:PlayerPet):
        self.battle_manager = battle_manager
        self.game_manager = self.battle_manager.player1.game_manager
        self.pet_loadout = pet_loadout
        self.enemy_loadout = self.battle_manager.loadouts[1] if self.battle_manager.loadouts[0] is pet_loadout else self.battle_manager.loadouts[0]
        self.effect_pet = effect_pet
        self.effect_str = self.effect_pet.pet.ability

class GameEffectInfo:
    """stores information about a game effect"""
    def __init__(self, game_manager:VersusGameManager, pet_loadout:Loadout, effect_pet:PlayerPet, client:Client):
        self.game_manager = game_manager
        self.pet_loadout = pet_loadout
        self.enemy_loadout = self.game_manager.loadouts[1] if self.game_manager.loadouts[0] is pet_loadout else self.game_manager.loadouts[0]
        self.effect_pet = effect_pet
        self.effect_str = self.effect_pet.pet.ability
        self.client = client