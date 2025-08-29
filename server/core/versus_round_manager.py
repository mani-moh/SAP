"""round manager class"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from entities.loadout import Loadout
    from core.versus_game_manager import VersusGameManager
import asyncio
from core.battle_manager import BattleManager
from entities.battle_result import BattleResult
from board.player import Player
from core.client import Client
from util import helpers
from core.shop_event_manager import ShopEventManager


class RoundManager:
    """manages a round of a game inclusing the shop phase and the battle phase between """
    def __init__(self, client1:Client, client2:Client, versus_game_manager:VersusGameManager):
        self.versus_game_manager = versus_game_manager
        self.loadouts: list[Loadout] = versus_game_manager.loadouts
        self.client1 = client1
        self.client2 = client2
        self.player1 = client1.player
        self.player2 = client2.player
        



    async def send_messages(self, message:dict, clients:list[Client]):
        await self.versus_game_manager.send_messages(message, clients)

    async def broadcast(self, message: dict):
        await self.versus_game_manager.broadcast(message)

    async def play_round(self):
        """plays a round of the game"""
        await self.shop_phase()
        self.battle_phase()
        self.next_round()

    async def shop_phase(self):
        """plays the shop phase of the game"""
        self.event_manager = ShopEventManager(self.versus_game_manager)
        for loadout in self.loadouts:
            for player_pet in loadout:
                if player_pet is not None:
                    func = player_pet.pet.ability_func
                    self.event_manager.subscribe(player_pet.pet.ability_class, func, player_pet)
                    for ability in player_pet.pet.secondary_abilities:
                        self.event_manager.subscribe(ability["ability_class"], ability["ability"], player_pet)
        self.player1.shop.reroll()
        self.player2.shop.reroll()
        self.client1.send_message({"type": "shop_update", "shop": str(self.player1.shop), "round": self.versus_game_manager.round})
        self.client2.send_message({"type": "shop_update", "shop": str(self.player2.shop), "round": self.versus_game_manager.round})
        print("waiting for ready")
        while not self.client1.go_to_battle_phase or not self.client2.go_to_battle_phase:
            await asyncio.sleep(0.5)

    def battle_phase(self):
        """plays the battle phase of the game"""
        self.battle_manager = BattleManager(self.player1, self.player2)
        result = self.battle_manager.battle()
        print(result)
        self.process_results(result)

    def process_results(self, result:BattleResult):
        """processes the results of the battle phase"""
        self.client1.send_message({"type": "battle_result", "result": str(result)})
        self.client2.send_message({"type": "battle_result", "result": str(result)})

    def next_round(self):
        self.versus_game_manager.round += 1
        self.client1.go_to_battle_phase = False
        self.client2.go_to_battle_phase = False
def test():
    player1 = Player("p1", 1)
    player2 = Player("p2", 2)
    round_manager = RoundManager(player1, player2)

    player1.loadout[1] = helpers.create_player_pet_from_json("Mosquito")
    player1.loadout[2] = helpers.create_player_pet_from_json("Dodo")
    player1.loadout[3] = helpers.create_player_pet_from_json("Skunk")
    player2.loadout[1] = helpers.create_player_pet_from_json("Crab")
    player2.loadout[2] = helpers.create_player_pet_from_json("Whale")
    player2.loadout[3] = helpers.create_player_pet_from_json("Dolphin")
    # player2.loadout[4] = helpers.create_pet_from_json("Dolphin")
    # player2.loadout[5] = helpers.create_pet_from_json("Dolphin")
    round_manager.battle_phase()