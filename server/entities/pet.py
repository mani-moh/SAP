"""pet class"""

class Pet():
    """
    Represents a base pet and its base stats to be used in player pet and shop pet.
    """
    def __init__(self, name, attack, health, tier, ability):
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
        self.name = name
        self.attack = attack
        self.health = health
        self.tier = tier
        self.ability = ability  # Ability class

    def __str__(self):
        return f'{self.name} (Attack:{self.attack}, Health:{self.health}, '\
               f'Tier:{self.tier}, Ability:{self.ability})'

