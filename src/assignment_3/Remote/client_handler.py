import asyncio
import logging
from operator import index
import socket
from time import sleep

from ..Common.api import Packet, Type


class ClientHandler:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 1238,
        protocol: str = "TCP",
        index: int = 0,
    ) -> None:

        if protocol not in (validProtocolList := ["TCP", "UDP", "MULTI"]):
            raise Exception(
                f"Invalid Protocol. {protocol} given. Expected {'/'.join(validProtocolList)}"
            )

        self._host = host
        self._port = port
        self._protocol = protocol
        self._addr = host, port
        self._index = index
    

        if protocol == "MULTI":
            self._send_queue = asyncio.Queue()

    async def connectAndListenToServerAsync(self):
        logging.debug(
            f"ClientHandler {self._index}: Trying to connect to TCP server on {self._host}:{self._port}"
        )
        while True:
            try:
                self._reader, self._writer = await asyncio.open_connection(*self._addr)
                break
            except:
                await asyncio.sleep(1)
        self.server_stopped = False
        clients_temp_address = self._writer.get_extra_info("sockname")
        logging.debug(
            f"Client: {self._index} connected to Server: from {clients_temp_address}"
        )
        asyncio.create_task(self._listenLoop())
        asyncio.create_task(self._sendLoop())

    async def _listenLoop(self):
        try:
            while True:
                incoming_bytes = await self._reader.readline()
                if not incoming_bytes: break
                serverMessage : Packet = self._decodeRawAndValidate(incoming_bytes)
                logging.debug(f"Remote ({self._index}) Server: {serverMessage.message}")
        except:
            pass
        self.server_stopped = True

    async def _sendLoop(self):
        try:
            while True:
                outgoing_bytes = await self._send_queue.get()
                self._writer.write(outgoing_bytes)
                await self._writer.drain()
        except:
            pass
        self._send_queue.task_done()
        self.server_stopped = True
        

    def startRemoteClient(self):
        if self._protocol == "TCP":
            socket.create_connection
            self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            logging.debug(
                f"ClientHandler {self._index}: Trying to connect to TCP server on {self._host}:{self._port}"
            )
            while True:
                try:
                    self._s.connect((self._host, self._port))
                    break
                except ConnectionRefusedError:
                    sleep(1)
            logging.debug(f"ClientHandler: connected to server")
        elif self._protocol == "UDP":
            self._s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def sendPacket(self, packet: Packet):
        if self.server_stopped:
            raise Exception("Server stopped")
        # logging.debug(f"ClientHandler {self._index}: sending {packet} to Server")
        if self._protocol == "TCP":
            self._s.sendall(packet.encode())
        elif self._protocol == "UDP":
            self._s.sendto(packet.encode(), self._addr)
        elif self._protocol == "MULTI":
            self._send_queue.put_nowait(packet.encode())
        
            



    def getServerMessage(self) -> str:
        rawBytes = b""
        if self._protocol == "TCP":
            rawBytes = self._s.makefile("rb").readline()
        elif self._protocol == "UDP":
            rawBytes, addr = self._s.recvfrom(1024)
            if addr != self._addr:
                return ""
        ip = self._decodeRawAndValidate(rawBytes)
        return ip.message or ""

    def _decodeRawAndValidate(self, messageRaw: bytes) -> Packet:
        ip = Packet.decode(messageRaw)
        if ip.type != Type.Server:
            raise Exception(
                f"ClientHandler: Unexpected Packet Type Received {ip.type}. Expected {Type.Server}"
            )
        return ip

    def close(self):
        self._s.close()
