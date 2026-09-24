from multiprocessing.synchronize import Event as EventType


def onlyWhenON(func):
    def wrapper(self, *args, **kwargs):
        if getattr(self, "state", True):
            return func(self, *args, **kwargs)
        raise Exception(f"TV is turned off. '{func.__name__}' is not allowed.")

    return wrapper


class SmartTV:
    def __init__(
        self, serverReadyEvent: EventType, host: str = "127.0.0.1", port: int = 1238, protocol:str = "TCP", channelCount: int = 3
    ):
        if channelCount < 3:
            raise ValueError("channelCount must be >= 3")
        self._channelCount = channelCount
        self._channel = 1
        self._state = True
        self._protocol = protocol
        self._serverReadyEvent = serverReadyEvent

    def start(self):
        from server_handler import ServerHandler
        self._serverHandler = ServerHandler(self, protocol=self._protocol)
        self._serverHandler.startServer(self._serverReadyEvent)
        

    def restartServer(self):
        self._serverHandler.stopServer()
        self._serverHandler.startServer(self._serverReadyEvent)
        self._channel = 1

    def turnOn(self):
        self._state = True

    def turnOff(self):
        self._state = False

    @property
    def state(self) -> bool:
        return self._state

    @property
    @onlyWhenON
    def channelCount(self) -> int:
        return self._channelCount

    @property
    @onlyWhenON
    def channel(self) -> int:
        return self._channel

    @channel.setter
    @onlyWhenON
    def channel(self, newChannel: int):
        if newChannel < 0:
            raise Exception("New Channel cannot be negative")
        channelToBe = newChannel % self.channelCount
        if channelToBe == 0:  # if newChannel%self.channelCount is 0
            self._channel = self.channelCount
        else:
            self._channel = channelToBe

    @onlyWhenON
    def moveChannelUp(self):
        self.channel += 1

    @onlyWhenON
    def moveChannelDown(self):
        self.channel -= 1
