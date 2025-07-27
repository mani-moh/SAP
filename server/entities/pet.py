"""pet class"""
from server.entities.effects import effect_lookup

class Pet():
    """
    Represents a base pet and its base stats to be used in player pet and shop pet.
    """
    def __init__(self, name:str, attack:int, health:int, tier:int, ability_class:str, ability:str, seconadry_abilities = []):
        """
        initializes a Pet
        
        :param name: name of the pet
        :type name: str
        :param attack: pet's attack value
        :type attack: int
        :param health: pet's health value
        :type health: int
        :param tier: pet's tier
        :type tier: int
        :param ability: pet's ability
        :type ability: Ability
        """
        self.name:str = name
        self.attack:int= attack
        self.health:int = health
        self.tier:int = tier
        self.ability_class:str = ability_class
        self.ability:str = ability  # Ability name
        self.ability_func = effect_lookup[self.ability] #the function itself
        self.secondary_abilities = seconadry_abilities
        self.swallowed:str = None

    def __str__(self):
        return f'{self.name} (Attack:{self.attack}, Health:{self.health}, '\
               f'Tier:{self.tier}, Ability:{self.ability})'

