"""battle manager class"""

class BattleManager:
    """ manages the battle between two loadouts"""

    def __init__(self, team1, team2):
        self.team1 = team1
        self.team2 = team2

    def battle(self):
        """starts the battle and returns the winner"""
        while not self.is_battle_over():
            self.attack_phase()
            self.resolve_deaths()
            self.resolve_after_death_abilities()
        return self.resolve_winner()
