import asyncio
import aiohttp
from .cache_classes import SmartCache_List

class SiteConnector():

    def __init__(self) -> None:
        self.BASIC_API_URL = 'http://127.0.0.1:8000/api/'
        self.session = None

    async def setup(self, maxsize: int = 128) -> None:
        self.session = aiohttp.ClientSession()
        print('Session is opened!')
        self.cache = SmartCache_List(maxsize)
        print(f'Cache created! Size: {maxsize}')

    async def get_data(self, ENDPOINT: str, quiet: bool = False):
        predict = await self.cache.get(ENDPOINT)
        if predict is not None:
            return predict
        try:
            async with self.session.get(self.BASIC_API_URL + ENDPOINT) as resp:
                if not quiet: print(f'[GET] -> {ENDPOINT} | {resp.status}')
                else: await self.cache.append(ENDPOINT, await resp.json())
                return await resp.json()
        except:
            return print(f'[GET] -> {ENDPOINT} | Error occured') 

    async def post_data(self, ENDPOINT: str, data: set):
        try:
            async with self.session.post(self.BASIC_API_URL + ENDPOINT, json=data) as resp:
                print(f'[POST] -> {ENDPOINT} | {resp.status}')
        except:
            return print(f'[POST] -> {ENDPOINT} | Error occured')

    async def put_data(self, ENDPOINT: str, data: set):
        try:
            async with self.session.put(self.BASIC_API_URL + ENDPOINT, json=data)  as resp:
                print(f'[PUT] -> {ENDPOINT} | {resp.status}')
        except:
            return print(f'[PUT] -> {ENDPOINT} | Error occured')

    async def reset(self, maxsize: int = 128, reason: str = 'No reason'):
        self.cache = SmartCache_List(maxsize)
        return print(f'Resetting cache with reason: {reason}\nNew Size: {maxsize}')

    async def cache_stats(self):
        return self.cache.stats()

    async def close_session(self, reason: str):
        print(f'Session will be closed in 10 seconds. Reason: {reason}')
        await asyncio.sleep(10)
        await self.session.close()
        return await asyncio.sleep(1)