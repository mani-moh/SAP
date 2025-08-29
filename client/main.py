import asyncio
import json
import copy

async def listen_server(reader: asyncio.StreamReader):
    """Listen for messages from the server."""
    while True:
        data = await reader.readline()
        if not data:
            print("Server closed the connection.")
            break
        message = json.loads(data.decode())
        if message["type"] == "text":
            print(f"\nReceived: {message['text']}\nEnter message: ", end="")
        elif message["type"] == "shop_update":
            msg = json.loads(message["shop"])
            pets = []
            for str_pet in msg:
                pets.append(json.loads(str_pet))
            pets2 = []
            for pet in pets:
                dic = copy.deepcopy(pet)
                dic["pet info"] =  json.loads(pet["pet info"])
                pets2.append(dic)
            print(f"Round {message['round']}, Shop: {pets2}")
        else:
            print(f"\nReceived: {message}\nEnter message: ", end="")

async def send_server(writer: asyncio.StreamWriter):
    """Send messages to the server from user input."""
    running = True
    while running:
        user_input = await asyncio.to_thread(input, "Enter message: ")
        # wrap user input in a dict to send as JSON
        if user_input == "join versus queue":
            msg = {"type":"join versus queue"}
        elif user_input == "ready":
            msg = {"type":"ready"}
        else:
            msg = {"type":"text", "text": user_input}
        writer.write((json.dumps(msg) + "\n").encode())
        await writer.drain()
        print(f"sent: {msg}")

async def main():
    reader, writer = await asyncio.open_connection('localhost', 5000)

    # Run listener and sender concurrently
    # await asyncio.gather(
    #     listen_server(reader),
    #     send_server(writer)
    # )
    t1 = asyncio.create_task(listen_server(reader))
    t2 = asyncio.create_task(send_server(writer))
    await asyncio.gather(t1,t2)

if __name__ == "__main__":
    asyncio.run(main())