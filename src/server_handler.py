import logging
import socket

from api import Packet, Command, Type
from smart_tv import SmartTV
from multiprocessing.synchronize import Event as EventType

class ServerHandler:

    def __init__(
        self,
        smartTV: SmartTV,
        host: str = "localhost",
        port: int = 1238,
        protocol:str = "TCP"
    ) -> None:

        from TransportProtocol import TCPTransport, UDPTransport

        if protocol == "TCP":
            self._transportProtocol = TCPTransport(self, host, port)
        elif protocol == "UDP":
            self._transportProtocol = UDPTransport(self, host, port)
        self._tv = smartTV

    def startServer(self, serverReadyEvent:EventType):
        self._transportProtocol.startServer(serverReadyEvent)

    def stopServer(self):
        self._transportProtocol.close()

    def processMessage(self, message: bytes) -> bytes:
        packet = Packet.decode(message)
        if packet.type != Type.Client:
            raise Exception("Invalid protocol type")
        return self._processPacket(packet).encode()

    def _processPacket(self, packet: Packet) -> Packet:
        tv = self._tv
        respondMsg = ""
        try:
            match packet.commandCode:
                case Command.ON:
                    tv.turnOn()
                    respondMsg = "TV turned on"
                case Command.OFF:
                    tv.turnOff()
                    respondMsg = "TV turned off"
                case Command.UP:
                    tv.moveChannelUp()
                    respondMsg = f"Channel moved up to {tv.channel}"
                case Command.DOWN:
                    tv.moveChannelDown()
                    respondMsg = f"Channel moved down to {tv.channel}"
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
                        respondMsg = f"Channel is set to {tv.channel}"
                    else:
                        respondMsg = f"No channel is provided"
                case _:
                    respondMsg = f"'{packet.commandCode}' is unknown"

        except Exception as e:
            respondMsg = "ServerHandler Error: " + str(e)

        respondMsg = "TV: " + respondMsg
        return Packet(Type.Server, Command.MESSAGE, message=respondMsg)
