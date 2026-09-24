import logging

from client_handler import ClientHandler
from api import Packet, Command, Type


class Remote:

    def __init__(self, host: str = "localhost", port: int = 1238, protocol:str = "TCP") -> None:
        self._host = host
        self._port = port
        self._protocol = protocol
        

    def start(self):
        self._clientHandler = ClientHandler(self._host, self._port, protocol=self._protocol)
        self._clientHandler.startRemoteClient()

    def _sendCommand(self, commandCode: Command, args: str = ""):

        outPacket = Packet(type=Type.Client, commandCode=commandCode, args=args)
        self._clientHandler.sendPacket(outPacket)
        # logging.debug(f"Remote: sending Command.{commandCode.name}")
        logging.debug(self._clientHandler.getServerMessage())

    def moveChannelUp(self):
        self._sendCommand(Command.UP)

    def moveChannelDown(self):
        self._sendCommand(Command.DOWN)

    def turnOnTV(self):
        self._sendCommand(Command.ON)

    def turnOffTV(self):
        self._sendCommand(Command.OFF)

    def channels(self):
        self._sendCommand(Command.CHANNELS)

    def set_channel(self, channel: int):
        self._sendCommand(Command.SET_CHANNEL, args=str(channel))

    def status(self):
        self._sendCommand(Command.STATUS)

    def shutdown(self):
        logging.debug("Remote: shutting down")
        self._clientHandler.close()
