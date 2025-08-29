"""shop class"""
import json
import config
from util.helpers import create_random_shop_pet_from_json
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from board.player import Player
    from entities.shop_pet import ShopPet

class Shop():
    def __init__(self, index:int, player):
        """
        Initializes a Shop
        """
        self.shop_pets:list[ShopPet] = []
        self.player:Player = player
        self.index = index
        self.tiers_unlock = config.tiers_unlock
        self.reroll_pet_counts = config.reroll_pet_counts
        self.reroll_food_counts = config.reroll_food_counts
        self.current_reroll_pet_count = self.get_shop_pet_slots(1)
        self.current_reroll_food_count = self.get_shop_food_slots(1)
        self.current_tier = self.get_current_tier(1)

    def __str__(self):
        result = []
        for shop_pet in self.shop_pets:
            result.append(str(shop_pet))
        return json.dumps(result)

    def get_shop_pet_slots(self, round):
        slots = self.reroll_pet_counts[0][1]
        for start_round, count in self.reroll_pet_counts:
            if round >= start_round:
                slots = count
            else:
                break
        return slots

    def get_shop_food_slots(self, round):
        slots = self.reroll_food_counts[0][1]
        for start_round, count in self.reroll_food_counts:
            if round >= start_round:
                slots = count
            else:
                break
        return slots
    def get_current_tier(self,round):
        current_tier = 1
        for tier in self.tiers_unlock:
            if round >= self.tiers_unlock[tier]:
                current_tier = self.tiers_unlock[tier]
            else:
                break
        return current_tier

    def reroll(self):
        self.shop_pets = [pet for pet in self.shop_pets if pet.is_frozen()]
        self.current_reroll_pet_count = self.get_shop_pet_slots(self.player.game_manager.round)
        self.current_reroll_food_count = self.get_shop_food_slots(self.player.game_manager.round)
        self.current_tier = self.get_current_tier(self.player.game_manager.round)
        for _ in range(self.current_reroll_pet_count-len(self.shop_pets)):
            shop_pet = create_random_shop_pet_from_json(self.current_tier)
            self.shop_pets.append(shop_pet)