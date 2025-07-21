"""Player pet class"""

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

        self.pet = pet
        self.xp = xp
        self.level = level

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
