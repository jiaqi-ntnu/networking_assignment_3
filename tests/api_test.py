import pytest
from src.api import Packet, Type, Command  # Update import path as needed

e_type = Type.Client
e_command = Command.MESSAGE
e_msg = "xdd"


@pytest.fixture
def packet():
    return Packet(e_type, e_command, message=e_msg)


def testIntEnums():
    assert Type.Client == 0x00
    assert Command.CHANNELS == 0x05


def testInit(packet):
    assert packet.type == e_type
    assert packet.commandCode == e_command
    assert packet.type == e_type
    assert packet.args == ""


def testEncode(packet):
    encoded = packet.encode()
    assert str(int(e_type)).encode() in encoded
    assert str(int(e_command)).encode() in encoded
    assert e_msg.encode() in encoded


def testDecode(packet):
    encoded = packet.encode()
    decoded = Packet.decode(encoded)
    assert decoded == packet