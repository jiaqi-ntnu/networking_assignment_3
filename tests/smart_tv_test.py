import multiprocessing
import pytest
from src.smart_tv import SmartTV

e_channelCount = 3


@pytest.fixture
def tv(e_channelCount=e_channelCount):
    event = multiprocessing.Event()
    return SmartTV(serverReadyEvent=event, channelCount=e_channelCount)


def testInitialState(tv):
    assert tv.state is True
    assert tv.channel == 1
    assert tv.channelCount == e_channelCount


def testInitialStateInvalid():
    event = multiprocessing.Event()
    with pytest.raises(ValueError, match="channelCount must be >= 3"):
        SmartTV(serverReadyEvent=event, channelCount=2)


def testOff(tv):
    tv.turnOff()
    assert tv.state is False


def testOn(tv):
    tv.turnOff()
    tv.turnOn()
    assert tv.state is True


def testMoveChannelUp(tv):
    assert tv.channel == 1
    tv.moveChannelUp()
    assert tv.channel == 2
    tv.moveChannelUp()
    assert tv.channel == 3
    # tests wrap around
    tv.moveChannelUp()
    assert tv.channel == 1


def testMoveChannelDown(tv):
    assert tv.channel == 1
    # tests wrap around
    tv.moveChannelDown()
    assert tv.channel == 3
    tv.moveChannelDown()
    assert tv.channel == 2
    tv.moveChannelDown()
    assert tv.channel == 1


def testSetChannelValid(tv):
    tv.channel = 2
    assert tv.channel == 2
    tv.channel = 3
    assert tv.channel == 3
    tv.channel = 1
    assert tv.channel == 1
    tv.channel = 4
    assert tv.channel == 1
    tv.channel = 5
    assert tv.channel == 2
    tv.channel = 0
    assert tv.channel == 3


def testSetChannelInValid(tv):
    with pytest.raises(Exception, match="New Channel cannot be negative"):
        tv.channel = -1


def test_only_when_on_decorator(tv):
    tv.turnOff()

    # tests getting channel count
    with pytest.raises(Exception, match="TV is turned off"):
        _ = tv.channelCount

    # tests getting current channel
    with pytest.raises(Exception, match="TV is turned off"):
        _ = tv.channel

    # tests setting channel
    with pytest.raises(Exception, match="TV is turned off"):
        tv.channel = 2

    # tests moving channel up
    with pytest.raises(Exception, match="TV is turned off"):
        tv.moveChannelUp()

    # tests moving channel down
    with pytest.raises(Exception, match="TV is turned off"):
        tv.moveChannelDown()

    tv.turnOn()
    tv.channel = 1
    assert tv.channel == 1
