import asyncio
import json
import copy
import pygame
import os
import config

from entities.versus_game_manager import VersusGameManager
class Client:
    def __init__(self):
        self.host = config.HOST
        self.port = config.PORT
        self.sender_queue = asyncio.Queue()
        self.versus_game_manager = None
        self.pygame_running = False
        self.current_state = "menu"
        self.game_state = None
        self.ready = False
        self.buying = False
        self.selected_type = None
        self.selected_index = None
        self.current_round = 1
        self.current_lives = 3
        self.current_enemy_lives = 3
        self.coins = 10
        self.listen_running = True
        self.send_running = True
        self.sender_running = True
    async def run(self):
        self.reader, self.writer = await asyncio.open_connection('localhost', 5000)

        # Run listener and sender concurrently
        # await asyncio.gather(
        #     listen_server(reader),
        #     send_server(writer)
        # )
        t1 = asyncio.create_task(self.listen_server(self.reader))
        t2 = asyncio.create_task(self.send_server(self.writer))
        t3 = asyncio.create_task(self.pygame_loop())
        await asyncio.gather(t1,t2,t3)
    async def listen_server(self, reader: asyncio.StreamReader):
        """Listen for messages from the server."""
        while self.listen_running:
            data = await reader.readline()
            if not data:
                print("Server closed the connection.")
                break
            # print(f"Received: {data.decode()}")
            message = json.loads(data.decode())
            match message["type"]:
                case "text":
                    print(f"\nReceived: {message['text']}\nEnter message: ", end="")
                case "shop_update":
                    self.selected_type = None
                    self.selected_index = None
                    self.versus_game_manager.pet_shop = message['shop']['shop']
                    print(f"shop:{self.versus_game_manager.pet_shop}")

                    
                    self.versus_game_manager.pets[1] = message['loadout']['pet1']
                    self.versus_game_manager.pets[2] = message['loadout']['pet2']
                    self.versus_game_manager.pets[3] = message['loadout']['pet3']
                    self.versus_game_manager.pets[4] = message['loadout']['pet4']
                    self.versus_game_manager.pets[5] = message['loadout']['pet5']
                    

                    print(f"loadout:{self.versus_game_manager.pets}")
                    self.current_round = message['round']
                    self.current_lives = message['lives']
                    self.current_enemy_lives = message['enemy lives']
                    self.coins = message['coins']
                case "start versus match":
                    self.current_state = "versus game"
                    self.game_state = "shop"
                    index = message["index"]
                    game_id = message["game id"]
                    self.versus_game_manager = VersusGameManager(game_id, index)
                case "battle_result":
                    d = recursive_json_loads(data.decode())
                    with open("games.json", 'w') as f:
                        json.dump(d, f, indent=4)
                    print(f"Battle result: {d}")

                    self.ready = False
                case "end versus match":
                    self.current_state = "menu"
                    self.game_state = None
                    self.selected_type = None
                    self.selected_index = None
                    self.buying = False
                    self.versus_game_manager = None
                case _:
                    print(f"\nReceived: {message}\nEnter message: ", end="")

    async def send_server(self, writer: asyncio.StreamWriter):
        """Send messages to the server from user input."""
        asyncio.create_task(self.message_sender())
        while self.send_running:
            user_input = await asyncio.to_thread(input, "Enter message: ")
            # wrap user input in a dict to send as JSON
            if user_input == "join versus queue":
                msg = {"type":"join versus queue"}
            elif user_input == "ready":
                msg = {"type":"ready"}
                self.selected_type = None
                self.selected_index = None
            else:
                msg = {"type":"text", "text": user_input}
            self.send_message(msg)

    async def message_sender(self):
        while self.sender_running:
            msg = await self.sender_queue.get()
            final = json.dumps(msg) + "\n"
            self.writer.write(final.encode())
            await self.writer.drain()
            self.sender_queue.task_done()
            print(f"msg sent:{msg}\nEnter message: ", end="")

    def send_message(self, msg):
        self.sender_queue.put_nowait(msg)

    async def pygame_loop(self):
        pygame.init()
        
        pygame.font.init()
        font1 = pygame.font.Font(None, 20)
        font2 = pygame.font.Font(None, 50)

        screen = pygame.display.set_mode((800, 600))
        clock = pygame.time.Clock()
        images = self.load_images_from_folder("images")
        self.pygame_running = True
        while self.pygame_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.pygame_running = False
                    self.listen_running = False
                    self.send_running = False
                    self.sender_running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.current_state == "menu":
                        rect = pygame.Rect(config.versus)
                        if rect.collidepoint(event.pos):
                            self.current_state = "versus queue"
                            self.send_message({"type": "join versus queue"})
                    if self.current_state == "versus game":
                        if self.game_state == "shop":
                            if self.ready == False:
                                for i,pet in enumerate(self.versus_game_manager.pet_shop):
                                    rect = pygame.Rect(30 + i*100, 420, 80, 80)
                                    if rect.collidepoint(event.pos):
                                        if self.selected_type == "shop pet" and self.selected_index == i and self.buying == False:
                                            self.selected_type = None
                                            self.selected_index = None
                                        else:
                                            self.selected_type = "shop pet"
                                            self.selected_index = i
                                for i in self.versus_game_manager.pets:
                                    pet = self.versus_game_manager.pets[i]
                                    rect = pygame.Rect(30 + (i-1)*100, 220, 80, 80)
                                    if rect.collidepoint(event.pos):
                                        if self.selected_type == "pet" and self.selected_index == i:
                                            if self.buying == False:
                                                self.selected_type = None
                                                self.selected_index = None
                                            
                                        else:
                                            if pet is not None:
                                                if self.buying == False:
                                                    self.selected_type = "pet"
                                                    self.selected_index = i
                                                else:
                                                    if self.versus_game_manager.pets[i] is None or self.versus_game_manager.pets[i]['pet']['name'] == self.versus_game_manager.pet_shop[self.selected_index]['pet']['name']:
                                                        msg = {"type":"buy pet", "pos": i, "shop index":self.selected_index}
                                                        self.selected_type = None
                                                        self.selected_index = None
                                                        self.buying = False
                                                        self.send_message(msg)
                                            else:
                                                if self.buying == True:
                                                    if self.versus_game_manager.pets[i] is None or self.versus_game_manager.pets[i]['pet']['name'] == self.versus_game_manager.pet_shop[self.selected_index]['pet']['name']:
                                                        msg = {"type":"buy pet", "pos": i, "shop index":self.selected_index}
                                                        self.selected_type = None
                                                        self.selected_index = None
                                                        self.buying = False
                                                        self.send_message(msg)
                                rect = pygame.Rect(config.freeze)
                                if self.selected_type == "shop pet" and rect.collidepoint(event.pos):
                                    msg = {"type":"freeze", "game id":self.versus_game_manager.game_id, "pos": self.selected_index}
                                    self.send_message(msg)
                                
                                rect = pygame.Rect(config.ready)
                                if rect.collidepoint(event.pos):
                                    msg = {"type":"ready"}
                                    self.selected_type = None
                                    self.selected_index = None
                                    self.ready = True
                                    self.send_message(msg)
                                
                                rect = pygame.Rect(config.reroll)
                                if self.selected_type in (None, "pet") and self.coins>0 and rect.collidepoint(event.pos):
                                    
                                    self.selected_type = None
                                    self.selected_index = None
                                    msg = {"type":"reroll"}
                                    self.send_message(msg)
                                
                                rect = pygame.Rect(config.sell)
                                if self.selected_type == "pet" and rect.collidepoint(event.pos):
                                    msg = {"type":"sell", "pos": self.selected_index}
                                    self.send_message(msg)
                                    self.selected_type = None
                                    self.selected_index = None
                                
                                rect = pygame.Rect(config.buy)
                                if self.selected_type == "shop pet" and self.coins>2 and rect.collidepoint(event.pos):
                                    self.buying = True
                                
                                rect = pygame.Rect(config.cancel)
                                if rect.collidepoint(event.pos):
                                    self.selected_type = None
                                    self.selected_index = None
                                    self.buying = False

            #DRAW----------------------------------------------
            screen.fill(config.colors["white"])

            if self.selected_type == "shop pet":
                pygame.draw.circle(screen, (255, 222, 33), (70+self.selected_index*100, 460), 50)
            if self.selected_type == "pet":
                pygame.draw.circle(screen, (255, 222, 33), (70+(self.selected_index-1)*100, 260), 50)
            if self.current_state == "menu":
                sap_text = font2.render("SAP Clone", True, config.colors["orange"])
                pygame.draw.rect(screen, config.colors["orange"], config.versus)
                versus_text = font2.render("Versus Game", True, config.colors["black"])
                screen.blit(versus_text, (config.versus[0] + 10, config.versus[1] + 10))
                screen.blit(sap_text, (350, 10))
            elif self.current_state == "versus game":
                if self.game_state == "shop":
                    current_round = font1.render(f"Round: {self.current_round}", True, config.colors["black"])
                    current_lives = font1.render(f"Lives: {self.current_lives}", True, config.colors["black"])
                    enemy_lives = font1.render(f"Enemy Lives: {self.current_enemy_lives}", True, config.colors["black"])
                    coins = font1.render(f"Coins: {self.coins}", True, config.colors["black"])
                    screen.blit(current_round, (10, 10))
                    screen.blit(current_lives, (90, 10))
                    screen.blit(enemy_lives, (170, 10))
                    screen.blit(coins, (300, 10))
                    if self.ready == False:
                        if self.selected_type == "shop pet":
                            if self.buying == False:
                                pygame.draw.rect(screen, config.colors["orange"], config.buy)
                                pygame.draw.rect(screen, config.colors["orange"], config.freeze)
                                pygame.draw.rect(screen, config.colors["dark orange"], config.sell)
                                pygame.draw.rect(screen, config.colors["dark orange"], config.cancel)
                                pygame.draw.rect(screen, config.colors["orange"], config.ready)
                                pygame.draw.rect(screen, config.colors["dark orange"], config.reroll)
                            else:
                                pygame.draw.rect(screen, config.colors["dark orange"], config.buy)
                                pygame.draw.rect(screen, config.colors["dark orange"], config.freeze)
                                pygame.draw.rect(screen, config.colors["dark orange"], config.sell)
                                pygame.draw.rect(screen, config.colors["orange"], config.cancel)
                                pygame.draw.rect(screen, config.colors["dark orange"], config.ready)
                                pygame.draw.rect(screen, config.colors["dark orange"], config.reroll)

                        elif self.selected_type == "pet":
                            pygame.draw.rect(screen, config.colors["orange"], config.sell)
                            pygame.draw.rect(screen, config.colors["dark orange"], config.buy)
                            pygame.draw.rect(screen, config.colors["dark orange"], config.freeze)
                            pygame.draw.rect(screen, config.colors["dark orange"], config.cancel)
                            pygame.draw.rect(screen, config.colors["orange"], config.ready)
                            pygame.draw.rect(screen, config.colors["orange"], config.reroll)
                            
                        else:
                            pygame.draw.rect(screen, config.colors["dark orange"], config.buy)
                            pygame.draw.rect(screen, config.colors["dark orange"], config.freeze)
                            pygame.draw.rect(screen, config.colors["dark orange"], config.sell)
                            pygame.draw.rect(screen, config.colors["dark orange"], config.cancel)
                            pygame.draw.rect(screen, config.colors["orange"], config.ready)
                            pygame.draw.rect(screen, config.colors["orange"], config.reroll)

                    else:
                        pygame.draw.rect(screen, config.colors["dark orange"], config.sell)
                        pygame.draw.rect(screen, config.colors["dark orange"], config.buy)
                        pygame.draw.rect(screen, config.colors["dark orange"], config.freeze)
                        pygame.draw.rect(screen, config.colors["dark orange"], config.cancel)
                        pygame.draw.rect(screen, config.colors["dark orange"], config.ready)
                        pygame.draw.rect(screen, config.colors["dark orange"], config.reroll)

                    buy_text = font1.render("BUY", False, config.colors["black"])
                    sell_text = font1.render("SELL", False, config.colors["black"])
                    freeze_text = font1.render("FREEZE", False, config.colors["black"])
                    cancel_text = font1.render("CANCEL", False, config.colors["black"])
                    ready_text = font1.render("END TURN", False, config.colors["black"])
                    reroll_text = font1.render("REROLL", False, config.colors["black"])
                    screen.blit(buy_text,(config.buy[0] + 39, config.buy[1] + 8))
                    screen.blit(sell_text,(config.sell[0] + 35, config.sell[1] + 8))
                    screen.blit(freeze_text,(config.freeze[0] + 25, config.freeze[1] + 8))
                    screen.blit(cancel_text,(config.cancel[0] + 25, config.cancel[1] + 8))
                    screen.blit(ready_text,(config.ready[0] + 25, config.ready[1] + 8))
                    screen.blit(reroll_text,(config.reroll[0] + 25, config.reroll[1] + 8))
                if self.versus_game_manager:
                    for i,pet in enumerate(self.versus_game_manager.pet_shop):
                        text_surface = font1.render(f"{pet['pet']['name']}\na:{pet['pet']['attack']} h:{pet['pet']['health']} price:{pet['price']}", True, config.colors["black"])
                        screen.blit(text_surface, (30 + i*100, 400))
                        if pet['pet']['name'].lower() in images:
                            if pet['frozen']:
                                screen.blit(images["ice"], (20 + i*100, 410))
                            screen.blit(images[pet['pet']['name'].lower()], (30 + i*100, 420))
                        else:
                            t2 = font1.render("image not found", True, config.colors["black"])
                            screen.blit(t2, (30 + i*100, 420))
                    for i in self.versus_game_manager.pets:
                        pet = self.versus_game_manager.pets[i]
                        pygame.draw.rect(screen, config.colors["black"], (30 + (i-1)*100, 280, 60, 10))
                        if pet is None:
                            continue
                        text_surface = font1.render(f"{pet['pet']['name']}\na:{pet['pet']['attack']} h:{pet['pet']['health']}", True, config.colors["black"])
                        screen.blit(text_surface, (30 + (i-1)*100, 200))
                        if pet['pet']['name'].lower() in images:
                            screen.blit(images[pet['pet']['name'].lower()], (30 + (i-1)*100, 220))
                        else:
                            t2 = font1.render("image not found", True, config.colors["black"])
                            screen.blit(t2, (30 + (i-1)*100, 220))
                    
            pygame.display.flip()
            #--------------------------------------------------
            await asyncio.sleep(0)
            clock.tick(60)
        pygame.quit()
        asyncio.get_running_loop().stop()



    def load_images_from_folder(self, folder: str) -> dict[str, pygame.Surface]:
        images = {}
        for filename in os.listdir(f"client/{folder}"):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                path = os.path.join(f"client/{folder}", filename)
                img = pygame.image.load(path).convert_alpha()
                if os.path.splitext(filename)[0] == "ice":
                    img = pygame.transform.scale(img, (100,100))
                else:
                    img = pygame.transform.scale(img, (80,80))
                images[os.path.splitext(filename)[0]] = img  # use name without extension
        return images
def recursive_json_loads(obj):
    if isinstance(obj, str):
        try:
            # Try parsing as JSON
            loaded = json.loads(obj)
            # If successful, recurse again
            return recursive_json_loads(loaded)
        except (json.JSONDecodeError, TypeError):
            # Not valid JSON -> leave as string
            return obj
    elif isinstance(obj, dict):
        return {k: recursive_json_loads(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [recursive_json_loads(item) for item in obj]
    else:
        return obj
if __name__ == "__main__":
    client = Client()
    asyncio.run(client.run())