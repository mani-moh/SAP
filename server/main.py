# from core import versus_round_manager
# versus_round_manager.test()
import asyncio
from core.versus_game_manager import VersusGameManager

if __name__ == "__main__":
    game_manager = VersusGameManager()
    asyncio.run(game_manager.run())