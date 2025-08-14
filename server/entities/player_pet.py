"""Player pet class"""
from __future__ import annotations
from entities.pet import Pet

class PlayerPet:
    """
    Represents a pet in a player's loadout
    """
    def __init__(self, pet, xp=0, level = 1):
        """
        Initializes a PlayerPet

        :param pet: the pet object associated with the player
        :type pet: pet.Pet
        :param xp: experience points of the player pet (default is 0)
        :type xp: int
        :param level: level of the player pet (default is 1)
        :type level: int
        """

        
        self.pet : Pet = pet
        self.xp = xp
        self.level = level
        self.alive = True

    def __str__(self):
        return f'{self.pet} (XP:{self.xp}, Level:{self.level})'

    def add_xp(self, xp):
        """
        adds xp to the player pet
        """
        new_xp = self.xp + xp
        if new_xp in (0,1,2,3,4,5):
            if new_xp in (0, 1):
                self.level = 1
            elif new_xp in (2, 3, 4):
                self.level = 2
            elif new_xp in (5,):
                self.level = 3
            self.xp = new_xp
            return True
        return False

    def reset_xp(self):
        """
        resets the player pet's xp to 0 & level to 1
        """
        self.xp = 0
        self.level = 1

    def take_damage(self, damage:int = 1):
        """applies damage to pet and sets if the pet is still alive"""
        self.pet.health -= damage
        if self.pet.health <= 0:
            self.alive = False
            self.pet.health = 0
    
    def heal(self, healing:int = 1):
        """heals the pet"""
        self.pet.health += healing

    def set_health(self, health:int = 1):
        """sets the pet's health"""
        self.pet.health = health
        if self.pet.health <= 0:
            self.alive = False

    def damage_amount(self) -> int:
        """returns the damage amount"""
        #TODO check if there is a damage modifier
        return self.pet.attack
