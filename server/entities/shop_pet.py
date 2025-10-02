"""shop pet class"""
import config
import json
class ShopPet:
    """
    Represents a pet that is in the shop
    """
    def __init__(self, pet, frozen=False):
        """
        Initializes a ShopPet
        :param pet: pet that is being sold
        :type pet: Pet
        :param price: price of the pet
        :type price: int
        :param frozen: whether the pet is frozen or not
        :type frozen: bool
        """
        self.pet = pet
        self.price = config.default_pet_price
        self.frozen = frozen

    def __str__(self):
        info = {"pet info":str(self.pet), "price":self.price, "frozen":self.frozen}
        result = json.dumps(info)
        return result

    def freeze_toggle(self):
        """Freezes the pet so it won't be rerolled"""
        if self.frozen:
            self.frozen = False
        else:
            #TODO implement freeze cost
            self.frozen = True

    def unfreeze(self):
        """unfreezes the pet so it can be rerolled"""
        self.frozen = False

    def is_frozen(self):
        """returns whether the pet is frozen or not"""
        return self.frozen

    def buy(self):
        #TODO implement buying
        """Executes the purchase of the pet, applying any necessary effects or changes."""
        self.unfreeze()

    def to_dict(self):
        return {"pet":self.pet.to_dict(), "price":self.price, "frozen":self.frozen}