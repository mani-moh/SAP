import json
from pathlib import Path
from entities.pet import Pet
from entities.player_pet import PlayerPet
def create_pet_from_json(name):
    json_path = Path(__file__).parent.parent / "data" / "pets.json"
    with open(json_path, "r") as file:
        data = json.load(file)
    if name in data:
        pet_data = data[name]
        secondary_abilities = []
        if "secondary_abilities" in pet_data:
            for ability in pet_data["secondary_abilities"]:
                secondary_abilities.append(ability)
        pet = PlayerPet(Pet(pet_data["name"], pet_data["attack"], pet_data["health"], 1, pet_data["ability_class"], pet_data["ability"], secondary_abilities))
        return pet
    