# python3
# -- coding: utf-8 --
# -------------------------------
# @Author : Terry
# @File : rate_limit.py.py
# @Time : 2024/10/15 下午6:27
# -------------------------------
from fastapi import HTTPException
from config import get_config
import asyncio
from aiocache import cached
from aiocache.serializers import PickleSerializer


class RateLimiter:
    def __init__(self):
        self.limits = {}

    @cached(ttl=3600, serializer=PickleSerializer())
    async def get_limit(self, model: str):
        model_rate = get_config(model, "40/3h")
        limit, duration = model_rate.split("/")
        return int(limit), self.parse_duration(duration)

    def parse_duration(self, duration: str) -> float:
        value = float(duration[:-1])
        unit = duration[-1]
        return value * 3600 if unit == 'h' else value * 60 if unit == 'm' else value

    async def acquire(self, token: str, model: str):
        limit, per = await self.get_limit(model)
        key = f"{token}|{model}"

        if key not in self.limits:
            self.limits[key] = asyncio.Semaphore(limit)

        try:
            await asyncio.wait_for(self.limits[key].acquire(), timeout=0.1)
        except asyncio.TimeoutError:
            raise HTTPException(status_code=429, detail=f"Rate limit exceeded for {model}. Limit: {limit} requests per {per} seconds.")

        asyncio.create_task(self.release_after_delay(key, per))

    async def release_after_delay(self, key: str, delay: float):
        await asyncio.sleep(delay)
        self.limits[key].release()


async def get_rate_limit():
    return RateLimiter()