from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    
    from board.player import Player
class Client:
    def __init__(self, id, reader:asyncio.StreamReader, writer:asyncio.StreamWriter):
        self.id = id
        self.name = f"p{id}"
        self.reader = reader
        self.writer = writer
        self.player: Player = None
        self.go_to_battle_phase = False
        self.sender_queue = asyncio.Queue()
    def send_message(self, msg):
        
        self.sender_queue.put_nowait(msg)