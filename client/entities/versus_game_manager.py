class VersusGameManager():
    def __init__(self, game_id:int, player_index:int):
        self.game_id = game_id
        self.player_index = player_index
        self.pets = {1: None, 2: None, 3: None, 4: None, 5: None}
        self.pet_shop: list = []
        self.food_shop: list = []

