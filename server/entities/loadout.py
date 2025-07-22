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