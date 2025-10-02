import json
import random
from pathlib import Path
from entities.pet import Pet
from entities.player_pet import PlayerPet
from entities.shop_pet import ShopPet
def create_player_pet_from_json(name):
    json_path = Path(__file__).parent.parent / "data" / "pets.json"
    with open(json_path, "r") as file:
        data = json.load(file)
    if name in data:
        pet_data = data[name]
        secondary_abilities = []
        if "secondary_abilities" in pet_data:
            for ability in pet_data["secondary_abilities"]:
                secondary_abilities.append(ability)
        pet = PlayerPet(Pet(pet_data["name"], pet_data["attack"], pet_data["health"], pet_data["tier"], pet_data["ability_class"], pet_data["ability"], secondary_abilities))
        return pet
def create_random_shop_pet_from_json(max_tier):
    json_path = Path(__file__).parent.parent / "data" / "pets.json"
    with open(json_path, "r") as file:
        data = json.load(file)
    pet_data = data[random.choice([key for key in data.keys() if data[key]["tier"] <= max_tier])]
    secondary_abilities = []
    if "secondary_abilities" in pet_data:
        for ability in pet_data["secondary_abilities"]:
            secondary_abilities.append(ability)
    pet = ShopPet(Pet(pet_data["name"], pet_data["attack"], pet_data["health"], pet_data["tier"], pet_data["ability_class"], pet_data["ability"], secondary_abilities))
    return pet

def get_last_id(dictionary:dict):
    id = 0
    for key in dictionary:
        if key > id:
            id = key + 1
    return id
def recursive_json_loads(obj):
    if isinstance(obj, str):
        try:
            # Try parsing as JSON
            loaded = json.loads(obj)
            # If successful, recurse again
            return recursive_json_loads(loaded)
        except (json.JSONDecodeError, TypeError):
            # Not valid JSON -> leave as string
            return obj
    elif isinstance(obj, dict):
        return {k: recursive_json_loads(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [recursive_json_loads(item) for item in obj]
    else:
        return obj
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        return super().default(obj)