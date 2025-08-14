"""event manager class"""
from entities.player_pet import PlayerPet
from entities.battle_effect_info import BattleEffectInfo

class EventManager:
    """Manages the event"""
    def __init__(self, battle_manager):
        self.listeners = {}
        self.battle_manager = battle_manager

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
                print(f"loadout1:{self.battle_manager.battle_loadout1}")
                print(f"loadout2:{self.battle_manager.battle_loadout2}\n")
                info = BattleEffectInfo(self.battle_manager, self.battle_manager.which_loadout(event["player_pet"]), event["player_pet"])
                event["callback"](info, **kwargs)