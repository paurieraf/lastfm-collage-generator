import os
import sqlite3
import threading
import time
from collections import OrderedDict
from typing import Dict, Optional, Tuple

CACHE_KIND_ALBUM = "album"
CACHE_KIND_ARTIST = "artist"
CACHE_KINDS = (CACHE_KIND_ALBUM, CACHE_KIND_ARTIST)

DEFAULT_CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "lastfm-collage")
DEFAULT_DB_NAME = "artwork.db"
DEFAULT_LRU_MAXSIZE = 256

DEFAULT_TTL_SECONDS: Dict[str, int] = {
    CACHE_KIND_ALBUM: 30 * 24 * 60 * 60,
    CACHE_KIND_ARTIST: 7 * 24 * 60 * 60,
}


class ArtworkCache:
    """Two-tier artwork cache.

    Tier 1 is an in-memory LRU store (``OrderedDict``); Tier 2 is a
    persistent SQLite database stored under the user cache directory.
    All access is serialized through a single lock so the cache is safe
    to use from the tile download worker threads.
    """

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        lru_maxsize: int = DEFAULT_LRU_MAXSIZE,
        ttl_override_days: Optional[int] = None,
        db_name: str = DEFAULT_DB_NAME,
    ) -> None:
        self.cache_dir = cache_dir if cache_dir is not None else DEFAULT_CACHE_DIR
        self.db_name = db_name
        self.lru_maxsize = max(1, int(lru_maxsize))
        self._ttl_seconds: Dict[str, int] = dict(DEFAULT_TTL_SECONDS)
        if ttl_override_days is not None:
            override_seconds = int(ttl_override_days) * 24 * 60 * 60
            self._ttl_seconds = {kind: override_seconds for kind in self._ttl_seconds}

        self._lru: "OrderedDict[str, Tuple[bytes, float]]" = OrderedDict()
        self._lock = threading.Lock()
        self._conn: Optional[sqlite3.Connection] = None
        self._disk_enabled = False
        self._init_disk()

    def _init_disk(self) -> None:
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            db_path = os.path.join(self.cache_dir, self.db_name)
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.execute(
                "CREATE TABLE IF NOT EXISTS artwork ("
                "key TEXT PRIMARY KEY,"
                "data BLOB NOT NULL,"
                "fetched_at REAL NOT NULL,"
                "kind TEXT NOT NULL"
                ")"
            )
            conn.commit()
            self._conn = conn
            self._disk_enabled = True
        except (OSError, sqlite3.Error):
            self._conn = None
            self._disk_enabled = False

    def _ttl_for(self, kind: str) -> int:
        return self._ttl_seconds.get(kind, self._ttl_seconds[CACHE_KIND_ALBUM])

    def _trim_lru(self) -> None:
        while len(self._lru) > self.lru_maxsize:
            self._lru.popitem(last=False)

    def _purge_expired(self) -> None:
        if not self._disk_enabled or self._conn is None:
            return
        oldest = int(max(self._ttl_seconds.values()))
        cutoff = time.time() - oldest
        try:
            self._conn.execute("DELETE FROM artwork WHERE fetched_at < ?", (cutoff,))
            self._conn.commit()
        except sqlite3.Error:
            pass

    def get(self, key: str, kind: str) -> Optional[bytes]:
        with self._lock:
            data: Optional[bytes] = None
            if key in self._lru:
                self._lru.move_to_end(key)
                cached_data, cached_at = self._lru[key]
                if time.time() - cached_at <= self._ttl_for(kind):
                    return cached_data
                del self._lru[key]

            if self._disk_enabled and self._conn is not None:
                try:
                    row = self._conn.execute(
                        "SELECT data, fetched_at FROM artwork WHERE key = ?", (key,)
                    ).fetchone()
                except sqlite3.Error:
                    row = None
                if row is not None:
                    blob, fetched_at = row
                    if time.time() - fetched_at <= self._ttl_for(kind):
                        data = bytes(blob)
                    else:
                        try:
                            self._conn.execute(
                                "DELETE FROM artwork WHERE key = ?", (key,)
                            )
                            self._conn.commit()
                        except sqlite3.Error:
                            pass

            if data is not None:
                self._lru[key] = (data, time.time())
                self._trim_lru()
            return data

    def set(self, key: str, data: bytes, kind: str) -> None:
        with self._lock:
            self._lru[key] = (data, time.time())
            self._trim_lru()
            if self._disk_enabled and self._conn is not None:
                try:
                    self._conn.execute(
                        "INSERT OR REPLACE INTO artwork "
                        "(key, data, fetched_at, kind) VALUES (?, ?, ?, ?)",
                        (key, sqlite3.Binary(data), time.time(), kind),
                    )
                    self._conn.commit()
                    self._purge_expired()
                except sqlite3.Error:
                    pass

    def close(self) -> None:
        with self._lock:
            if self._conn is not None:
                try:
                    self._conn.close()
                except sqlite3.Error:
                    pass
                self._conn = None
            self._disk_enabled = False
