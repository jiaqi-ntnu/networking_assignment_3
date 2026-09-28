import logging
import multiprocessing

from .remote import Remote
from .smart_tv import SmartTV


def main(protocol:str = "TCP"):
    host = "127.0.0.1"
    port = 1238

    server_ready_event = multiprocessing.Event()

    tv = SmartTV(
        serverReadyEvent=server_ready_event, host=host, port=port, protocol=protocol
    )
    server_process = multiprocessing.Process(target=tv.start, daemon=True)
    server_process.start()

    server_ready_event.wait()
    rc = Remote(host, port, protocol=protocol)
    rc.start()
    rc.moveChannelUp()
    rc.moveChannelUp()
    rc.moveChannelUp()
    rc.moveChannelDown()
    rc.channels()
    rc.set_channel(1)
    rc.set_channel(-3)
    rc.status()
    rc.turnOffTV()
    rc.status()
    rc.moveChannelUp()
    rc.moveChannelDown()
    rc.set_channel(1)
    rc.shutdown()
