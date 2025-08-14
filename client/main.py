import asyncio
import json

async def listen_server(reader: asyncio.StreamReader):
    """Listen for messages from the server."""
    while True:
        data = await reader.readline()
        if not data:
            print("Server closed the connection.")
            break
        message = json.loads(data.decode().strip())
        print("Received:", message)

async def send_server(writer: asyncio.StreamWriter):
    """Send messages to the server from user input."""
    while True:
        user_input = await asyncio.to_thread(input, "Enter message: ")
        # wrap user input in a dict to send as JSON
        msg = {"type":"text", "text": user_input}
        writer.write((json.dumps(msg) + "\n").encode())
        await writer.drain()

async def main():
    reader, writer = await asyncio.open_connection('localhost', 5000)

    # Run listener and sender concurrently
    await asyncio.gather(
        listen_server(reader),
        send_server(writer)
    )

if __name__ == "__main__":
    asyncio.run(main())
