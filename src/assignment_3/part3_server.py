import asyncio
import multiprocessing
import random
from time import sleep

from assignment_3.Remote.remote import Remote
from assignment_3.TV.smart_tv import SmartTV

host = "127.0.0.1"
port = 1238
protocol = "TCP"


def startMultiTV(server_ready_event):
    tv = SmartTV(
        serverReadyEvent=server_ready_event, host=host, port=port, protocol=protocol
    )
    asyncio.run(tv.startMulti())


def startRemote(i):
    print("Starting remote", i)
    rc = Remote(host, port, protocol=protocol)
    rc.start()
    sleep(random.random())
    rc.moveChannelUp()
    sleep(random.random())
    rc.moveChannelUp()
    sleep(random.random())
    rc.moveChannelUp()
    sleep(random.random())
    rc.moveChannelDown()
    sleep(random.random())
    rc.channels()
    sleep(random.random())
    rc.set_channel(1)
    sleep(random.random())
    rc.set_channel(-3)
    sleep(random.random())
    rc.status()
    sleep(random.random())
    rc.turnOffTV()
    sleep(random.random())
    rc.status()
    sleep(random.random())
    rc.moveChannelUp()
    sleep(random.random())
    rc.moveChannelDown()
    sleep(random.random())
    rc.set_channel(1)
    sleep(random.random())
    rc.shutdown()


def part3_server():
    server_ready_event = multiprocessing.Event()
    startMultiTV(server_ready_event)
    # server_process = multiprocessing.Process(
    #     target=startMultiTV,
    #     kwargs={"server_ready_event": server_ready_event},
    #     daemon=True,
    # )
    # server_process.start()
    # server_ready_event.wait()


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    part3_server()
