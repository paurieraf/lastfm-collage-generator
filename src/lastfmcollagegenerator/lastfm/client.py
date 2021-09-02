from typing import List

import pylast
from pylast import User, TopItem


class LastfmClient:
    def __init__(self, api_key: str, api_secret: str):
        self.network = pylast.LastFMNetwork(
            api_key=api_key,
            api_secret=api_secret
        )

    def get_user(self, username: str) -> User:
        user = self.network.get_user(username)
        return user

    @staticmethod
    def get_top_albums(user: User, limit: int, period: str) -> List[TopItem]:
        """
        Returns a list of TopItems with the albums and the play count
        TODO: It will be necessary to do a custom request because pylast doesn't support page param in this query
        """
        top_albums = user.get_top_albums(period=period, limit=limit)
        return top_albums
