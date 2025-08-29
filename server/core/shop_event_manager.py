"""event manager in shop phase class"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.versus_game_manager import VersusGameManager
from entities.player_pet import PlayerPet
from entities.battle_effect_info import GameEffectInfo



class ShopEventManager:
    """Manages the events"""
    def __init__(self, game_manager):
        self.listeners: dict[str, list[dict]] = {}
        self.game_manager:VersusGameManager = game_manager

    def subscribe(self, event_type, callback, player_pet:PlayerPet):
        """Subscribes a callback to an event type"""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        event = {"callback": callback, "player_pet": player_pet}
        self.listeners[event_type].append(event)

    def post(self, event_type,**kwargs):
        """Posts an event"""
        if event_type in self.listeners:
            for event in self.listeners[event_type]:
                info = GameEffectInfo(self.game_manager, self.game_manager.which_loadout(event["player_pet"]), event["player_pet"])
                event["callback"](info, **kwargs)