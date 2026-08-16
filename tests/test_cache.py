import os

import pytest

from lastfmcollagegenerator.cache import (
    ArtworkCache,
    CACHE_KIND_ALBUM,
    CACHE_KIND_ARTIST,
    DEFAULT_LRU_MAXSIZE,
)


@pytest.fixture
def tmp_cache(tmp_path):
    return ArtworkCache(cache_dir=str(tmp_path / "cache"))


def test_cache_hit_avoids_refetch(tmp_cache):
    tmp_cache.set("https://mock.cdn/cover.png", b"PNGDATA", CACHE_KIND_ALBUM)
    assert tmp_cache.get("https://mock.cdn/cover.png", CACHE_KIND_ALBUM) == b"PNGDATA"


def test_cache_miss_returns_none(tmp_cache):
    assert tmp_cache.get("https://mock.cdn/missing.png", CACHE_KIND_ALBUM) is None


def test_expired_entry_is_not_returned(tmp_cache):
    expired = ArtworkCache(cache_dir=str(tmp_cache.cache_dir), ttl_override_days=0)
    expired.set("https://mock.cdn/old.png", b"OLD", CACHE_KIND_ALBUM)
    assert expired.get("https://mock.cdn/old.png", CACHE_KIND_ALBUM) is None


def test_cache_persists_across_instances(tmp_cache):
    tmp_cache.set("https://mock.cdn/persist.png", b"PERSIST", CACHE_KIND_ARTIST)
    tmp_cache.close()
    reloaded = ArtworkCache(cache_dir=tmp_cache.cache_dir)
    assert reloaded.get("https://mock.cdn/persist.png", CACHE_KIND_ARTIST) == b"PERSIST"


def test_artist_ttl_shorter_than_album_ttl(tmp_cache):
    album = ArtworkCache(cache_dir=str(tmp_cache.cache_dir), ttl_override_days=None)
    assert album._ttl_for(CACHE_KIND_ALBUM) > album._ttl_for(CACHE_KIND_ARTIST)


def test_lru_eviction_enforces_maxsize(tmp_path):
    cache = ArtworkCache(cache_dir=str(tmp_path / "lru"), lru_maxsize=2)
    cache.set("k1", b"1", CACHE_KIND_ALBUM)
    cache.set("k2", b"2", CACHE_KIND_ALBUM)
    cache.set("k3", b"3", CACHE_KIND_ALBUM)
    assert len(cache._lru) <= 2
    assert "k1" not in cache._lru
    assert cache.get("k3", CACHE_KIND_ALBUM) == b"3"


def test_default_lru_maxsize_constant():
    assert DEFAULT_LRU_MAXSIZE == 256


def test_unwritable_cache_dir_degrades_gracefully(tmp_path):
    unwritable = str(tmp_path / "blocked")
    os.makedirs(unwritable)
    os.chmod(unwritable, 0o000)
    try:
        cache = ArtworkCache(cache_dir=os.path.join(unwritable, "sub"))
        assert cache._disk_enabled is False
        cache.set("https://mock.cdn/x.png", b"X", CACHE_KIND_ALBUM)
        assert cache.get("https://mock.cdn/x.png", CACHE_KIND_ALBUM) == b"X"
        assert cache.get("https://mock.cdn/other.png", CACHE_KIND_ALBUM) is None
    finally:
        os.chmod(unwritable, 0o755)


def test_ttl_override_applies_to_all_kinds(tmp_path):
    cache = ArtworkCache(cache_dir=str(tmp_path / "ttl"), ttl_override_days=1)
    assert cache._ttl_for(CACHE_KIND_ALBUM) == 24 * 60 * 60
    assert cache._ttl_for(CACHE_KIND_ARTIST) == 24 * 60 * 60
