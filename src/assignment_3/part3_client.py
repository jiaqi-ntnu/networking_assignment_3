import asyncio
import multiprocessing
import random
from time import sleep

from assignment_3.Remote.remote import Remote
from assignment_3.TV.smart_tv import SmartTV

host = "127.0.0.1"
port = 1238
protocol = "MULTI"


def startRemote(i):
    asyncio.run(_startRemote(i))

async def _startRemote(i):
    print("Starting remote", i)
    rc = Remote(host, port, protocol=protocol, index=i)
    
    await rc.startAsync()
    commands = [
        rc.turnOnTV,
        rc.turnOffTV,
        rc.moveChannelUp,
        rc.moveChannelDown,
        rc.channels,
        rc.status,
        lambda: rc.set_channel(
            random.randint(-3, 6)
        ),  # Handles set_channel with a random channel number
    ]
    
    while True:
        action = random.choice(commands)
        action()
        await asyncio.sleep(random.uniform(0.5, 2.0)) 


def _init_worker():
    # if multiprocessing.current_process().name.endswith("-1") or :
    import logging

    logging.basicConfig(level=logging.DEBUG, format="%(message)s")


def part3_client():
    with multiprocessing.Pool(initializer=_init_worker) as pool:
        pool.map(startRemote, range(5))


if __name__ == "__main__":
    part3_client()
