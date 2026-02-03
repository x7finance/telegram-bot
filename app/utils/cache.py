import asyncio
import time
import inspect
from typing import Any, Optional


class CacheEntry:
    def __init__(self, value: Any, ttl: int):
        self.value = value
        self.expires_at = time.time() + ttl

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class Cache:
    def __init__(self):
        self._cache: dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None

            if entry.is_expired():
                del self._cache[key]
                return None

            return entry.value

    async def set(self, key: str, value: Any, ttl: int):
        async with self._lock:
            self._cache[key] = CacheEntry(value, ttl)

    async def delete(self, key: str):
        async with self._lock:
            if key in self._cache:
                del self._cache[key]

    async def clear(self):
        async with self._lock:
            self._cache.clear()


_global_cache = Cache()


def get_cache() -> Cache:
    return _global_cache


class CachedService:
    def __init__(self):
        super().__init__()
        self._cache = get_cache()
        self._class_name = self.__class__.__name__
        self._wrap_methods()

    def _wrap_methods(self):
        for name in dir(self):
            if name.startswith("_"):
                continue

            method = getattr(self, name)
            if callable(method) and asyncio.iscoroutinefunction(method):
                sig = inspect.signature(method)
                if "cache_ttl" in sig.parameters:
                    wrapped = self._create_cached_method(method)
                    setattr(self, name, wrapped)

    def _create_cached_method(self, method):
        method_name = method.__name__
        cache = self._cache
        class_name = self._class_name
        sig = inspect.signature(method)
        cache_ttl_param = sig.parameters.get("cache_ttl")
        default_ttl = (
            cache_ttl_param.default
            if cache_ttl_param
            and cache_ttl_param.default is not inspect.Parameter.empty
            else None
        )

        async def cached_method(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            ttl = bound.arguments.get("cache_ttl", default_ttl)

            if ttl is None or ttl == 0:
                return await method(*args, **kwargs)

            key_parts = [class_name, method_name]
            for i, (param_name, param) in enumerate(sig.parameters.items()):
                if i == 0:
                    continue
                if param_name == "cache_ttl":
                    continue
                if i < len(args):
                    key_parts.append(str(args[i]))
                elif param_name in kwargs:
                    key_parts.append(f"{param_name}={kwargs[param_name]}")

            cache_key = ":".join(key_parts)

            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            result = await method(*args, **kwargs)
            await cache.set(cache_key, result, ttl)
            return result

        cached_method.__name__ = method_name
        cached_method.__doc__ = method.__doc__

        return cached_method

    async def cache_clear(self):
        await self._cache.clear()
