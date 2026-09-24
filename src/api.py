from dataclasses import dataclass, asdict
from enum import IntEnum
import json


class Type(IntEnum):
    Client = 0x00
    Server = 0x01


class Command(IntEnum):
    MESSAGE = 0x00
    ON = 0x01
    OFF = 0x02
    UP = 0x03
    DOWN = 0x04
    CHANNELS = 0x05
    SET_CHANNEL = 0x06
    STATUS = 0x07


@dataclass
class Packet:
    type: Type
    commandCode: Command
    message: str | None = ""
    args: str | None = ""

    def encode(self) -> bytes:
        return json.dumps(asdict(self)).encode()

    @classmethod
    def decode(cls, payload: bytes) -> "Packet":
        return cls(**json.loads(payload.decode()))


if __name__ == "__main__":
    testPacket = Packet(Type.Client, Command.MESSAGE, message="xdd")
    print(testPacket)

    encoded = testPacket.encode()
    print(encoded)

    decoded = Packet.decode(encoded)
    print(decoded)
