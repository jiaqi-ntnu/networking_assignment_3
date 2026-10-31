import asyncio


async def coro_a():
    for _ in range(3):
        await asyncio.sleep(1)
        print("I am coro_a(). Hi!")


async def coro_b():
    await asyncio.sleep(0.3)
    print("I am coro_b(). I sure hope no one hogs the event loop...")


async def main():
    await asyncio.gather(coro_a(), coro_b())


asyncio.run(main())
