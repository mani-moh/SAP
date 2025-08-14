from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import asyncio
    from board.player import Player
class Client:
    def __init__(self, id, reader:asyncio.StreamReader, writer:asyncio.StreamWriter):
        self.id = id
        self.reader = reader
        self.writer = writer
        self.player: Player = None