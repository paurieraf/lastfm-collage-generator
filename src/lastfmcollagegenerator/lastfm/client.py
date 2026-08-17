import asyncio
import functools
from typing import Any, Callable, List, TypeVar

import pylast
from pylast import User, TopItem

T = TypeVar("T")


async def _to_thread(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    if hasattr(asyncio, "to_thread"):
        return await asyncio.to_thread(func, *args, **kwargs)
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))


class LastfmClient:
    def __init__(self, api_key: str, api_secret: str):
        self.network = pylast.LastFMNetwork(api_key=api_key, api_secret=api_secret)

    def get_user(self, username: str) -> User:
        user = self.network.get_user(username)
        return user

    async def get_user_async(self, username: str) -> User:
        """Asynchronously returns a User object."""
        return await _to_thread(self.get_user, username)

    @staticmethod
    def get_top_albums(user: User, limit: int, period: str) -> List[TopItem]:
        """Returns a list of TopItems with the albums and the play count."""
        top_albums = user.get_top_albums(period=period, limit=limit)
        return top_albums

    @classmethod
    async def get_top_albums_async(
        cls, user: User, limit: int, period: str
    ) -> List[TopItem]:
        """Asynchronously returns a list of TopItems with the albums and play count."""
        return await _to_thread(cls.get_top_albums, user, limit, period)

    @staticmethod
    def get_top_artists(user: User, limit: int, period: str) -> List[TopItem]:
        """Returns a list of TopItems with the artists and the play count."""
        top_artists = user.get_top_artists(period=period, limit=limit)
        return top_artists

    @classmethod
    async def get_top_artists_async(
        cls, user: User, limit: int, period: str
    ) -> List[TopItem]:
        """Asynchronously returns a list of TopItems with the artists and play count."""
        return await _to_thread(cls.get_top_artists, user, limit, period)

    @staticmethod
    def get_top_tracks(user: User, limit: int, period: str) -> List[TopItem]:
        """Returns a list of TopItems with the tracks and the play count."""
        top_tracks = user.get_top_tracks(period=period, limit=limit)
        return top_tracks

    @classmethod
    async def get_top_tracks_async(
        cls, user: User, limit: int, period: str
    ) -> List[TopItem]:
        """Asynchronously returns a list of TopItems with tracks and play count."""
        return await _to_thread(cls.get_top_tracks, user, limit, period)
