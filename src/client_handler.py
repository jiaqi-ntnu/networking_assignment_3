import logging
import socket

from api import Packet, Command, Type


class ClientHandler:
    def __init__(
        self, host: str = "127.0.0.1", port: int = 1238, protocol: str = "TCP"
    ) -> None:

        if protocol not in (validProtocolList := ["TCP", "UDP"]):
            raise Exception(
                f"Invalid Protocol. {protocol} given. Expected {"/".join(validProtocolList)}"
            )

        self._host = host
        self._port = port
        self._protocol = protocol
        self._addr = host, port

    def startRemoteClient(self):
        if self._protocol == "TCP":

            self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._s.connect((self._host, self._port))
            logging.debug(
                f"ClientHandler: connected to TCP server on {self._host}:{self._port}"
            )
        elif self._protocol == "UDP":
            self._s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def sendPacket(self, packet: Packet):
        logging.debug(f"ClientHandler: sending {packet} to Server")
        if self._protocol == "TCP":
            self._s.sendall(packet.encode())
        elif self._protocol == "UDP":
            self._s.sendto(packet.encode(), self._addr)

    def getServerMessage(self) -> str:
        rawBytes = bytes()
        if self._protocol == "TCP":
            rawBytes = self._s.recv(4096)
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
