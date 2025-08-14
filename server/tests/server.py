"""
Super Auto Pets - Minimal, well-commented Python example
Single-file project that can run as either server or client.

Features shown (minimal, educational):
- Simple server using asyncio + websockets to relay game state/chat
- Simple Pygame client implementing a tiny UI (pets as colored boxes)
- Networking runs in an asyncio loop on a background thread; main thread runs Pygame
- Thread-safe queues to pass messages between networking and game logic

Run:
    # install dependencies
    pip install pygame websockets

    # run server (on localhost:8765)
    python sap_pygame_network.py --server

    # run client (connects to localhost by default)
    python sap_pygame_network.py --client --name Alice

Notes for maintainers / newbies:
- This is NOT a full Super Auto Pets clone; it's a compact, maintainable skeleton
  showing how to integrate pygame with asyncio websockets and how to structure code
  so a beginner can extend it.
- Keep networking code (async) separate from game logic (sync). Communication between
  them goes over simple JSON messages passed via thread-safe queues.

"""

import argparse
import asyncio
import json
import logging
import random
import threading
import time
from queue import Queue, Empty

import pygame
import websockets

# ---------- Configuration ----------
SERVER_HOST = 'localhost'
SERVER_PORT = 8765

# ---------- Simple data model (easy to understand) ----------
class Pet:
    """Minimal pet representation. Add health/attack/abilities later."""
    def __init__(self, species: str, attack: int, health: int):
        self.species = species
        self.attack = attack
        self.health = health

    def to_dict(self):
        return {"species": self.species, "attack": self.attack, "health": self.health}

    @classmethod
    def from_dict(cls, d):
        return cls(d['species'], d['attack'], d['health'])


class PlayerState:
    """What we keep for each connected player. This is small and serialisable."""
    def __init__(self, name: str):
        self.name = name
        # store a tiny team of pets for demo
        self.team = [Pet('ant', 1, 1), Pet('sheep', 2, 2)]

    def to_dict(self):
        return {"name": self.name, "team": [p.to_dict() for p in self.team]}

    @classmethod
    def from_dict(cls, d):
        ps = cls(d['name'])
        ps.team = [Pet.from_dict(x) for x in d['team']]
        return ps


# ---------- SERVER (asyncio + websockets) ----------
# The server keeps a minimal world state (list of players), accepts new connections,
# receives JSON messages and broadcasts world updates. This is intentionally simple.

class SimpleServer:
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        self.host = host
        self.port = port
        # ws -> PlayerState.name mapping
        self.clients = {}  # websockets.WebSocketServerProtocol -> player name
        self.players = {}  # name -> PlayerState
        # protect server state with a normal asyncio.Lock (server runs in a single thread)
        self.lock = asyncio.Lock()

    async def handler(self, websocket):
        """Handle incoming websocket connection. Expect a 'join' message first."""
        try:
            msg = await websocket.recv()
            data = json.loads(msg)
            if data.get('type') != 'join':
                await websocket.send(json.dumps({'type': 'error', 'message': 'expected join'}))
                return
            name = data.get('name', f'guest{random.randint(1000,9999)}')

            async with self.lock:
                self.clients[websocket] = name
                # create a new player if not exists
                if name not in self.players:
                    self.players[name] = PlayerState(name)

            # send initial world state to the new client
            await websocket.send(json.dumps({'type': 'welcome', 'state': self.get_world_state()}))

            # notify everyone about the new player
            await self.broadcast({'type': 'player_joined', 'name': name, 'state': self.get_world_state()})

            # main receive loop for this client
            async for msg in websocket:
                data = json.loads(msg)
                await self.process_message(websocket, data)

        except websockets.ConnectionClosed:
            pass
        finally:
            async with self.lock:
                name = self.clients.pop(websocket, None)
                if name:
                    self.players.pop(name, None)
            await self.broadcast({'type': 'player_left', 'name': name, 'state': self.get_world_state()})

    def get_world_state(self):
        # compile a serialisable view of server players
        return {'players': [p.to_dict() for p in self.players.values()]}

    async def broadcast(self, message: dict):
        msg_text = json.dumps(message)
        to_remove = []
        async with self.lock:
            for ws in list(self.clients):
                try:
                    await ws.send(msg_text)
                except websockets.ConnectionClosed:
                    to_remove.append(ws)
            for ws in to_remove:
                self.clients.pop(ws, None)

    async def process_message(self, websocket, data: dict):
        # handle an example message types: 'chat' and 'update_team'
        t = data.get('type')
        if t == 'chat':
            # broadcast chat from this player
            name = self.clients.get(websocket, 'unknown')
            await self.broadcast({'type': 'chat', 'from': name, 'text': data.get('text', '')})
        elif t == 'update_team':
            # client asks to update its team. We trust it for this demo.
            name = self.clients.get(websocket)
            if name:
                ps = PlayerState.from_dict({'name': name, 'team': data.get('team', [])})
                async with self.lock:
                    self.players[name] = ps
                await self.broadcast({'type': 'player_updated', 'name': name, 'state': self.get_world_state()})
        else:
            await websocket.send(json.dumps({'type': 'error', 'message': f'unknown type {t}'}))

    async def run(self):
        logging.info('Starting server on %s:%d', self.host, self.port)
        async with websockets.serve(self.handler, self.host, self.port):
            await asyncio.Future()  # run forever


# ---------- CLIENT side networking (async) ----------
# We keep networking code isolated. It runs an asyncio loop in a background thread
# and communicates with the main (Pygame) thread by Queue objects.

class NetworkClient:
    def __init__(self, server_uri, in_queue: Queue, out_queue: Queue, name='guest'):
        self.server_uri = server_uri
        self.in_queue = in_queue   # messages FROM network -> game (main thread)
        self.out_queue = out_queue # messages FROM game -> network
        self.name = name
        self.ws = None
        self.loop = None
        self._stop = asyncio.Event()

    async def connect_and_run(self):
        # keep reconnecting on failures (simple exponential backoff)
        backoff = 1.0
        while not self._stop.is_set():
            try:
                async with websockets.connect(self.server_uri) as ws:
                    self.ws = ws
                    # send join
                    await ws.send(json.dumps({'type': 'join', 'name': self.name}))
                    # start receiver and sender tasks
                    receiver = asyncio.create_task(self.receiver(ws))
                    sender = asyncio.create_task(self.sender(ws))
                    await asyncio.wait([receiver, sender], return_when=asyncio.FIRST_COMPLETED)
                    # if we exit here, one of the tasks ended -> close/cleanup
                    receiver.cancel()
                    sender.cancel()
            except Exception as e:
                # push an error message to the game so the player sees it
                self.in_queue.put({'type': 'net_error', 'message': str(e)})
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 10.0)
        logging.info('network loop stopped')

    async def receiver(self, ws):
        # read messages from websocket and put them on the in_queue for game to consume
        async for msg in ws:
            try:
                data = json.loads(msg)
            except Exception:
                data = {'type': 'raw', 'text': msg}
            self.in_queue.put(data)

    async def sender(self, ws):
        # read outgoing messages from out_queue (threadsafe Queue) and send them
        # Use a tiny sleep to avoid busy waiting
        while True:
            try:
                message = self.out_queue.get(timeout=0.1)
            except Empty:
                # also check if we should stop
                if self._stop.is_set():
                    return
                await asyncio.sleep(0)  # yield control
                continue
            # message should be serialisable
            await ws.send(json.dumps(message))

    def start_in_thread(self):
        # create a dedicated event loop in a new thread
        def _run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.connect_and_run())

        self._thread = threading.Thread(target=_run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        # tell the background loop to stop
        if self.loop and not self.loop.is_closed():
            # signal the coroutine to stop
            fut = asyncio.run_coroutine_threadsafe(self._stop.set(), self.loop)
            try:
                fut.result(timeout=1)
            except Exception:
                pass
        if hasattr(self, '_thread'):
            self._thread.join(timeout=1)


# ---------- Pygame client (main thread) ----------
# Very small UI: display player's name, their team, and a tiny chat input.

class SimpleGame:
    def __init__(self, network_in: Queue, network_out: Queue, player_name: str):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))
        pygame.display.set_caption('Mini SAP - Pygame + Asyncio Websockets')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.network_in = network_in
        self.network_out = network_out
        self.running = True
        self.player_name = player_name

        # local player state we can edit and push to server
        self.state = PlayerState(player_name)
        # world view from server
        self.world_state = {'players': []}
        # simple chat
        self.chat_lines = []
        self.chat_input = ''

    def draw_pet(self, pet: Pet, x, y):
        # draw pet as a colored rectangle and show stats
        rect = pygame.Rect(x, y, 120, 60)
        pygame.draw.rect(self.screen, (150, 200, 150), rect)
        txt = self.font.render(f'{pet.species} A{pet.attack} H{pet.health}', True, (0, 0, 0))
        self.screen.blit(txt, (x + 6, y + 6))

    def process_network_messages(self):
        # non-blocking: consume all queued network messages
        while True:
            try:
                msg = self.network_in.get_nowait()
            except Empty:
                break
            self.handle_network_message(msg)

    def handle_network_message(self, msg: dict):
        t = msg.get('type')
        if t == 'welcome' or t == 'player_joined' or t == 'player_left' or t == 'player_updated':
            self.world_state = msg.get('state', self.world_state)
        elif t == 'chat':
            self.chat_lines.append(f"{msg.get('from')}: {msg.get('text')}")
            if len(self.chat_lines) > 8:
                self.chat_lines.pop(0)
        elif t == 'net_error':
            self.chat_lines.append('[NET ERR] ' + msg.get('message', ''))
        else:
            # unknown messages are displayed for debugging
            self.chat_lines.append('[NET] ' + json.dumps(msg))
            if len(self.chat_lines) > 8:
                self.chat_lines.pop(0)

    def send_chat(self, text: str):
        self.network_out.put({'type': 'chat', 'text': text})

    def push_team_update(self):
        # tell the server about our team
        self.network_out.put({'type': 'update_team', 'team': [p.to_dict() for p in self.state.team]})

    def run(self):
        # push initial team
        self.push_team_update()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_RETURN:
                        if self.chat_input.strip():
                            self.send_chat(self.chat_input.strip())
                            self.chat_input = ''
                    elif event.key == pygame.K_b:
                        # 'b' to buy a random pet for simplicity
                        new_pet = Pet('bee', random.randint(1, 3), random.randint(1, 4))
                        self.state.team.append(new_pet)
                        self.push_team_update()
                    elif event.key == pygame.K_r:
                        # 'r' to remove last pet
                        if self.state.team:
                            self.state.team.pop()
                            self.push_team_update()
                    elif event.key == pygame.K_BACKSPACE:
                        self.chat_input = self.chat_input[:-1]
                    else:
                        # add typed character to chat
                        if event.unicode and len(event.unicode) == 1:
                            self.chat_input += event.unicode

            # process incoming network messages
            self.process_network_messages()

            # draw
            self.screen.fill((30, 30, 40))
            title = self.font.render(f'Player: {self.player_name}  (press B to buy, R remove, Enter to send chat)', True, (220, 220, 220))
            self.screen.blit(title, (8, 8))

            # draw our team on the left
            left_y = 50
            self.screen.blit(self.font.render('Your team:', True, (200, 200, 200)), (8, left_y))
            left_y += 24
            for pet in self.state.team:
                self.draw_pet(pet, 8, left_y)
                left_y += 72

            # draw world players on the right
            right_x = 360
            right_y = 50
            self.screen.blit(self.font.render('World players:', True, (200, 200, 200)), (right_x, right_y))
            right_y += 24
            for p in self.world_state.get('players', []):
                pname = p.get('name')
                self.screen.blit(self.font.render(pname, True, (220, 220, 220)), (right_x, right_y))
                right_y += 20
                for petd in p.get('team', []):
                    petobj = Pet.from_dict(petd)
                    self.draw_pet(petobj, right_x, right_y)
                    right_y += 72
                right_y += 8

            # draw chat area
            chat_y = 360
            for i, line in enumerate(self.chat_lines[-6:]):
                self.screen.blit(self.font.render(line, True, (200, 200, 200)), (8, chat_y + i * 18))
            # chat input
            self.screen.blit(self.font.render('> ' + self.chat_input, True, (255, 255, 255)), (8, 460 - 24))

            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()


# ---------- CLI and glue ----------

def run_server_forever(host=SERVER_HOST, port=SERVER_PORT):
    server = SimpleServer(host, port)
    asyncio.run(server.run())


def run_client(name, server_host=SERVER_HOST, server_port=SERVER_PORT):
    server_uri = f'ws://{server_host}:{server_port}'
    in_q = Queue()
    out_q = Queue()

    # start network client on background thread
    client = NetworkClient(server_uri, in_q, out_q, name=name)
    client.start_in_thread()

    # start pygame game in main thread
    game = SimpleGame(in_q, out_q, name)
    try:
        game.run()
    finally:
        client.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', action='store_true')
    parser.add_argument('--client', action='store_true')
    parser.add_argument('--host', default=SERVER_HOST)
    parser.add_argument('--port', default=SERVER_PORT, type=int)
    parser.add_argument('--name', default='guest')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.server:
        # run server on the chosen host/port
        SERVER_HOST = args.host
        SERVER_PORT = args.port
        run_server_forever(SERVER_HOST, SERVER_PORT)
    elif args.client:
        run_client(args.name, server_host=args.host, server_port=args.port)
    else:
        print('Specify --server or --client')
