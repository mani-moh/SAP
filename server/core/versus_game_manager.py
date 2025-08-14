"""game manager class"""
import socket
import json
import asyncio
from entities.loadout import Loadout
from board.player import Player
from core.client import Client
from core.versus_round_manager import RoundManager
class VersusGameManager:
    """Manages a versus game session"""
    Host = 'localhost'
    PORT = 5000
    def __init__(self, Host=Host, PORT=PORT):
        self.Host = Host
        self.PORT = PORT
        self.clients = []
        self.game_in_progress = False
        self.player1: Player = None
        self.player2: Player = None
        self.winner = None
        

    async def broadcast(self, message: dict):
            """Broadcasts a message to all clients"""
            for client in self.clients:
                if isinstance(client, Client):
                    client.writer.write(json.dumps(message).encode())
                    await client.writer.drain()

    async def run(self):
        server = await asyncio.start_server(
            lambda r,w: self.handle_client(r,w),
            host=self.Host,
            port=self.PORT
        )
        print(f"Server started at {server.sockets[0].getsockname()}")
        async with server:
            await server.serve_forever()

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        id = 1 if len(self.clients) == 0 else 2 if len(self.clients) == 1 else None
        if id is None:
            return
        client = Client(id, reader, writer)
        self.clients.append(client)
        print(f"Player {id} connected.")
        await self.broadcast({"info": f"Player {id} has joined."})
        if len(self.clients) == 2:
            await asyncio.gather(
                self.start_game(),
                self.receive_messages(self.clients[0]),
                self.receive_messages(self.clients[1])
            )
            # asyncio.create_task(self.start_game())
            # asyncio.create_task(self.receive_messages(self.clients[0]))
            # asyncio.create_task(self.receive_messages(self.clients[1]))
            # await asyncio.Event().wait()
        return

    async def receive_messages(self, client):
        try:
            if isinstance(client, Client):
                while True:
                    data = await client.reader.readline()
                    if not data:
                        return
                    data = json.loads(data.decode())
                    self.process_message(data, client)
        except asyncio.CancelledError:
            print("Client disconnected Cancelled error.")
        finally:
            print(f"Player {client.player.loadout.index} disconnected.")
            client.writer.close()
            await client.writer.wait_closed()

    def process_message(self, data, client: Client):
        match data['type']:
            case "text":
                print(f"Player {client.player.loadout.index} said: {data['text']}")


    async def start_game(self):
        self.game_in_progress = True
        self.player1 = Player("p1", 1)
        self.player2 = Player("p2", 2)
        self.clients[0].player = self.player1
        self.clients[1].player = self.player2
        round_manager = RoundManager(self.player1, self.player2)
        await asyncio.sleep(0.5)
        while not self.is_game_over():
            
            round_manager.play_round()

    def is_game_over(self):
        if self.player1.lives <= 0:
            self.winner = self.player2
            return True
        elif self.player2.lives <= 0:
            self.winner = self.player1
            return True
        return False