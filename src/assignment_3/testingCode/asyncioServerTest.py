import asyncio
from asyncio import StreamReader, StreamWriter

server_address = "localhost", 12345


async def handleClient_Echo(reader: StreamReader, writer: StreamWriter):
    addr = writer.get_extra_info("peername")
    print(f"Client connected from {addr}!")
    try:
        while True:
            incoming_bytes = await reader.read(1024)
            if not incoming_bytes:
                break
            client_message = incoming_bytes.decode()

            print(f"Received: {client_message} from {addr}")
            outgoingMessage = "Echo: " + client_message
            print(f"Sending: {outgoingMessage}")
            writer.write(outgoingMessage.encode())
            await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()

    print(f"Client  {addr} disconnected")


async def startAsyncIOEchoServer():
    server = await asyncio.start_server(
        handleClient_Echo, *server_address, reuse_address=True
    )
    print(f"Server started on {server_address}")
    async with server:
        await server.serve_forever()


asyncio.run(startAsyncIOEchoServer())
