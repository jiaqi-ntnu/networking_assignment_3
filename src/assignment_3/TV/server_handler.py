import asyncio
from asyncio import StreamReader, StreamWriter
from multiprocessing.synchronize import Event as EventType

from ..Common.api import Command, Packet, Type
from .smart_tv import SmartTV


class ServerHandler:
    def __init__(
        self,
        smartTV: SmartTV,
        host: str = "localhost",
        port: int = 1238,
        protocol: str = "TCP",
    ) -> None:

        from .ServerTransportProtocol import TCPTransport, UDPTransport

        if protocol == "TCP":
            self._transportProtocol = TCPTransport(self, host, port)
        elif protocol == "UDP":
            self._transportProtocol = UDPTransport(self, host, port)
        self._tv = smartTV
        self._addr = host, port
        self._clients = set()

    def startServer(self, serverReadyEvent: EventType):
        self._transportProtocol.startServer(serverReadyEvent)

    def stopServer(self):
        self._transportProtocol.close()

    async def startTCPMultiServer(self, serverReadyEvent: EventType):
        server = await asyncio.start_server(
            self._handleClient, *self._addr, reuse_address=True
        )
        print(f"Server started on {self._addr}")
        serverReadyEvent.set()
        async with server:
            await server.serve_forever()

    async def _broadcast(self, message_bytes: bytes):
        if not self._clients:
            return
        tasks = [self._sendToClient(writer, message_bytes) for writer in self._clients]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _sendToClient(self, writer: StreamWriter, message_bytes: bytes):
        try:
            writer.write(message_bytes)
            await writer.drain()
        except:
            self._clients.discard(writer)

    async def _handleClient(self, reader: StreamReader, writer: StreamWriter):
        client_addr = writer.get_extra_info("peername")
        self._clients.add(writer)
        print(f"Remote connected from {client_addr}!")
        try:
            while True:
                incoming_bytes = await reader.readline()
                if not incoming_bytes:
                    break
                print(f"Received: {incoming_bytes!r} from {client_addr}")
                response_bytes, is_broadcast = self.processMessage(incoming_bytes)
                if is_broadcast:
                    print(f"Broadcasting: {response_bytes!r}")
                    await self._broadcast(response_bytes)
                else:
                    print(f"Sending: {response_bytes!r}")
                    await self._sendToClient(writer, response_bytes)
        finally:
            self._clients.discard(writer)
            writer.close()
            try:
                await writer.wait_closed()
            except:
                pass  # Client disconnected abruptly (WinError 64 on Windows)

        print(f"Client  {client_addr} disconnected")

    def processMessage(self, message: bytes) -> tuple[bytes, bool]:
        packet = Packet.decode(message)
        if packet.type != Type.Client:
            raise Exception("Invalid protocol type")
        tv = self._tv
        respondMsg = ""
        is_broadcast = False
        try:  # add response
            match packet.commandCode:
                case Command.ON:
                    tv.turnOn()
                    respondMsg = "TV turned on"
                case Command.OFF:
                    tv.turnOff()
                    respondMsg = "TV turned off"
                case Command.UP:
                    tv.moveChannelUp()
                    respondMsg = f"Broadcast: Channel moved up to {tv.channel}"
                    is_broadcast = True
                case Command.DOWN:
                    tv.moveChannelDown()
                    respondMsg = f"Broadcast: Channel moved down to {tv.channel}"
                    is_broadcast = True
                case Command.STATUS:
                    respondMsg = (
                        f"TV is currently switched {'on' if tv.state else 'off'}"
                    )
                case Command.CHANNELS:
                    respondMsg = f"Channel is currently {tv.channel}"
                case Command.SET_CHANNEL:
                    if packet.args:
                        if packet.args.isdigit:
                            tv.channel = int(packet.args)
                        else:
                            raise TypeError(f"{packet.args} is not of int")
                        respondMsg = f"Broadcast: Channel is set to {tv.channel}"
                        is_broadcast = True
                    else:
                        respondMsg = "No channel is provided"
                case _:
                    respondMsg = f"'{packet.commandCode}' is unknown"

        except Exception as e:
            respondMsg = "ServerHandler Error: " + str(e)

        respondMsg = "TV: " + respondMsg
        return (
            Packet(Type.Server, Command.MESSAGE, message=respondMsg).encode(),
            is_broadcast,
        )
