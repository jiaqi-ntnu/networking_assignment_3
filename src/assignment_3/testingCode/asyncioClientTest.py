import asyncio
from random import random

server_address = "localhost", 12345

async def startAsyncIOClient(i):
    reader, writer = await asyncio.open_connection(*server_address)
    clients_temp_address = writer.get_extra_info("sockname")
    print(f"Connected to Server: {server_address} from {clients_temp_address}")
    try:
        while True:
            message = f"Client {i} spamming"
            print(f"Sending {message} to server")
            encoded_message = message.encode()
            writer.write(encoded_message)
            await writer.drain()
            incoming_bytes = await reader.read(1024)
            if not incoming_bytes:
                break
            server_message = incoming_bytes.decode()
            print(f"Server: {server_message}")

            sleepTiming = random()
            print(f"Client {i}: Sleeping for {sleepTiming}")
            await asyncio.sleep(sleepTiming)

    except Exception:
        print("Server forcibly disconnected")

    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    async with asyncio.TaskGroup() as tg:
        for i in range(3):
            tg.create_task(startAsyncIOClient(i))
    print("Server disconnected")

asyncio.run(main())
