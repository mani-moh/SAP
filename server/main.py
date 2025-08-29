# from core import versus_round_manager
# versus_round_manager.test()
# import asyncio
# from core.versus_game_manager import VersusGameManager

# if __name__ == "__main__":
#     game_manager = VersusGameManager()
#     asyncio.run(game_manager.run())
import asyncio
import json
from queue import Queue
from config import HOST, PORT
from core.client import Client
from core.versus_game_manager import VersusGameManager
class Server:
    def __init__(self):
        self.HOST = HOST
        self.PORT = PORT
        self.clients: list[Client] = []
        self.versus_queue = Queue()
        self.games: list[VersusGameManager] = []
        self.last_id = 0
        

    async def run(self):
        server = await asyncio.start_server(
            lambda r,w: self.handle_client(r,w),
            host=self.HOST,
            port=self.PORT
        )
        print(f"Server started at {server.sockets[0].getsockname()}")

        async with server:
            await server.serve_forever()

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        client_id = self.last_id + 1
        self.last_id = client_id
        client = Client(client_id, reader, writer)
        self.clients.append(client)
        print(f"Player {client_id} connected.")
        await self.broadcast({"type": "info", "info": f"Player {client_id} has joined."})
        asyncio.create_task(self.receive_messages(client))
        asyncio.create_task(self.message_sender(client))


    async def broadcast(self, message: dict):
        for client in self.clients:
            client.send_message(message)

    async def message_sender(self, client: Client):
        while True:
            msg = await client.sender_queue.get()
            final = json.dumps(msg) + "\n"
            client.writer.write(final.encode())
            await client.writer.drain()
            client.sender_queue.task_done()
            print(f"msg sent:{msg}")

    async def receive_messages(self, client:Client):
        try:
            if isinstance(client, Client):
                while True:
                    data = await client.reader.readline()
                    if not data:
                        return
                    data = json.loads(data.decode())
                    await self.process_message(data, client)
        except asyncio.CancelledError:
            print("Client disconnected Cancelled error.")
        finally:
            print(f"Player {client.id} disconnected.")
            client.writer.close()
            await client.writer.wait_closed()

    async def process_message(self, message:dict, client:Client):
        print(f"message recieved: {message}")
        match message['type']:
            case "text":
                print(f"Player {client.id} said: {message['text']}")
            case "join versus queue":
                self.versus_queue.put(client)
                print(f"Player {client.id} joined versus queue.")
                print(f"Players in queue: {self.versus_queue.qsize()}")
                asyncio.create_task(self.attempt_start_game())
            case "change name":
                client.name = message["name"]
                print(f"Player {client.id} changed name to {client.name}.")
            case "reroll":
                client.player.shop.reroll()
                client.send_message({"type": "shop_update", "shop": str(client.player.shop), "round": client.player.game_manager.round})
            case "ready":
                client.go_to_battle_phase = not client.go_to_battle_phase
                


    async def send_messages(self, message:dict, clients:list[Client]):
        for client in clients:
            client.send_message(message)

    async def continuous_check_queue(self):
        while True:
            self.attempt_start_game()
            await asyncio.sleep(1)

    async def attempt_start_game(self):
        if self.versus_queue.qsize() >= 2:
            client1 = self.versus_queue.get()
            client2 = self.versus_queue.get()
            versus_game_manager = VersusGameManager(client1, client2, self)
            await versus_game_manager.start_game()
            await self.send_messages([client1, client2], {"type":"event", "event": "start versus"})
async def main():
    server = Server()
    await server.run()
if __name__ == "__main__":
    asyncio.run(main())
