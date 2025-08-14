# client.py
import asyncio
import websockets
import json
import pygame

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("SAP Clone Test")

state = {"gold": 10, "pets": []}

async def game_client():
    global state
    async with websockets.connect("ws://localhost:8765") as websocket:

        async def sender():
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_b:  # Press B to buy pet
                            await websocket.send(json.dumps({
                                "action": "buy_pet"
                            }))
                        elif event.key == pygame.K_SPACE:  # Space = start battle
                            await websocket.send(json.dumps({
                                "action": "start_battle"
                            }))

                # Render
                screen.fill((0, 0, 0))
                font = pygame.font.SysFont(None, 30)
                text = font.render(f"Gold: {state['gold']}", True, (255, 255, 255))
                screen.blit(text, (20, 20))
                pygame.display.flip()

                await asyncio.sleep(0.016)  # ~60 FPS

        async def receiver():
            while True:
                message = await websocket.recv()
                data = json.loads(message)

                if data["event"] == "state_update":
                    state = data["state"]

                elif data["event"] == "battle_result":
                    print("Battle log:", data["log"])
                    print("Winner:", data["winner"])

        await asyncio.gather(sender(), receiver())

if __name__ == "__main__":
    asyncio.run(game_client())
