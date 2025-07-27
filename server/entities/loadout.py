"""loadout class"""

from server.entities.player_pet import PlayerPet

class Loadout:
    """Represents a player's loadout"""
    index_range = (1,2,3,4,5)
    def __init__(self):
        """
        Initializes a Loadout

        :param pet1: player pet 1
        :type pet1: PlayerPet
        :param pet2: player pet 2
        :type pet2: PlayerPet
        :param pet3: player pet 3
        :type pet3: PlayerPet
        """
        self.pet1: PlayerPet = None
        self.pet2: PlayerPet = None
        self.pet3: PlayerPet = None
        self.pet4: PlayerPet = None
        self.pet5: PlayerPet = None
    
    def __iter__(self):
        yield self.pet1
        yield self.pet2
        yield self.pet3
        yield self.pet4
        yield self.pet5

    def __getitem__(self, index) -> PlayerPet:
        if not index in self.index_range:
            raise IndexError("Index out of range")
        return getattr(self, f"pet{index}")

    def __setitem__(self, index, value):
        if not index in self.index_range:
            raise IndexError("Index out of range")
        setattr(self, f"pet{index}", value)

    def is_empty(self):
        """returns whether the loadout is empty or not"""
        for pet in self:
            if pet is not None:
                return False
        return True

    def swap(self, pos1, pos2):
        """swaps two positions on a loadout"""
        if pos1 not in self.index_range or pos2 not in self.index_range:
            raise IndexError("Index out of range")
        self[pos1], self[pos2] = self[pos2], self[pos1]

    def pet_indices(self):
        """returns the indices loadout that are not empty"""
        return [i for i in self.index_range if self[i] is not None]

    def healthiest_pet(self) -> PlayerPet:
        """returns the healthiest pet in the loadout as PlayerPet"""
        healthiest_ally = None
        for player_pet in self:
            if player_pet is not None and (healthiest_ally is None or player_pet.pet.health > healthiest_ally.pet.health):
                healthiest_ally = player_pet
        return healthiest_ally

    def weakest_pet(self) -> PlayerPet:
        """returns the weakest pet in the loadout as PlayerPet"""
        weakest_ally = None
        for player_pet in self:
            if player_pet is not None and (weakest_ally is None or player_pet.pet.health < weakest_ally.pet.health):
                weakest_ally = player_pet
        return weakest_ally

    def pet_index(self, player_pet:PlayerPet):
        """returns the index of the player pet in the loadout or None if not found"""
        for i in self.index_range:
            if self[i] is player_pet:
                return i

    def friend_ahead(self, player_pet:PlayerPet):
        """returns the player pet that is ahead of the player pet in the loadout or None if not found"""
        index = self.pet_index(player_pet)
        if index is None:
            return None
        if index == 1:
            return None
        index -= 1
        while index in self.index_range:
            if self[index] is not None:
                return self[index]
            index -= 1
        return None
