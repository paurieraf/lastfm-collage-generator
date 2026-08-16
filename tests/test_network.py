import time
from unittest.mock import MagicMock, patch

import pytest
import requests

from lastfmcollagegenerator.network import (
    CircuitBreaker,
    CircuitOpenError,
    FetchError,
    ResilientHttpFetcher,
    TokenBucket,
    retry_with_full_jitter,
)


def make_response(status_code=200, content=b""):
    resp = MagicMock()
    resp.status_code = status_code
    resp.content = content
    resp.raise_for_status.return_value = None
    return resp


def test_token_bucket_throttles_burst():
    bucket = TokenBucket(rate=5.0, capacity=5.0)
    for _ in range(5):
        bucket.acquire()
    start = time.monotonic()
    bucket.acquire()
    elapsed = time.monotonic() - start
    assert elapsed >= 0.15


def test_retry_then_succeed():
    calls = []

    def flaky():
        calls.append(1)
        if len(calls) < 2:
            raise requests.ConnectionError("transient")
        return make_response(200, b"ok")

    resp = retry_with_full_jitter(flaky, max_attempts=3, sleep_fn=lambda s: None)
    assert resp.status_code == 200
    assert len(calls) == 2


def test_retry_gives_up_after_max_attempts():
    calls = []

    def always_fails():
        calls.append(1)
        raise requests.ConnectionError("down")

    with pytest.raises(FetchError):
        retry_with_full_jitter(always_fails, max_attempts=3, sleep_fn=lambda s: None)
    assert len(calls) == 3


def test_retry_on_5xx_status():
    calls = []

    def server_error():
        calls.append(1)
        return make_response(503)

    with pytest.raises(FetchError):
        retry_with_full_jitter(server_error, max_attempts=2, sleep_fn=lambda s: None)
    assert len(calls) == 2


def test_retry_returns_non_transient_4xx_immediately():
    calls = []

    def not_found():
        calls.append(1)
        return make_response(404)

    resp = retry_with_full_jitter(not_found, max_attempts=3, sleep_fn=lambda s: None)
    assert resp.status_code == 404
    assert len(calls) == 1


def test_circuit_breaker_opens_after_threshold():
    breaker = CircuitBreaker(failure_threshold=2, cooldown_seconds=60.0)
    assert breaker.allow_request()
    breaker.record_failure()
    assert breaker.allow_request()
    breaker.record_failure()
    assert breaker.state == CircuitBreaker.OPEN
    assert not breaker.allow_request()


def test_circuit_breaker_half_open_recovery():
    breaker = CircuitBreaker(failure_threshold=2, cooldown_seconds=0.0)
    breaker.record_failure()
    breaker.record_failure()
    assert breaker.state == CircuitBreaker.OPEN
    assert breaker.allow_request()
    assert breaker.state == CircuitBreaker.HALF_OPEN
    breaker.record_success()
    assert breaker.state == CircuitBreaker.CLOSED
    assert breaker.allow_request()


def test_circuit_breaker_half_open_failure_reopens():
    breaker = CircuitBreaker(failure_threshold=2, cooldown_seconds=0.0)
    breaker.record_failure()
    breaker.record_failure()
    assert breaker.state == CircuitBreaker.OPEN
    assert breaker.allow_request()
    breaker.record_failure()
    assert breaker.state == CircuitBreaker.OPEN


def test_fetcher_retries_and_succeeds():
    calls = []

    def flaky(url, headers=None, timeout=None):
        calls.append(url)
        if len(calls) < 2:
            raise requests.ConnectionError("transient")
        return make_response(200, b"bytes")

    fetcher = ResilientHttpFetcher(
        rate_limit=None, sleep_fn=lambda s: None, request_fn=flaky
    )
    resp = fetcher.get("https://mock.cdn/art.png")
    assert resp.status_code == 200
    assert len(calls) == 2


def test_fetcher_fast_fails_when_circuit_opens():
    calls = []

    def failing(url, headers=None, timeout=None):
        calls.append(url)
        raise requests.ConnectionError("down")

    fetcher = ResilientHttpFetcher(
        rate_limit=None,
        max_attempts=3,
        sleep_fn=lambda s: None,
        request_fn=failing,
        failure_threshold=2,
    )
    with pytest.raises(FetchError):
        fetcher.get("https://mock.cdn/art.png")
    assert len(calls) == 2

    with pytest.raises(CircuitOpenError):
        fetcher.get("https://mock.cdn/art.png")
    assert len(calls) == 2


def test_fetcher_recovers_after_cooldown():
    calls = []

    def failing_then_ok(url, headers=None, timeout=None):
        calls.append(url)
        if len(calls) <= 2:
            raise requests.ConnectionError("down")
        return make_response(200, b"recovered")

    fetcher = ResilientHttpFetcher(
        rate_limit=None,
        max_attempts=3,
        sleep_fn=lambda s: None,
        request_fn=failing_then_ok,
        failure_threshold=2,
        cooldown_seconds=0.0,
    )
    with pytest.raises(FetchError):
        fetcher.get("https://mock.cdn/art.png")

    resp = fetcher.get("https://mock.cdn/art.png")
    assert resp.status_code == 200


def test_fetcher_uses_module_requests_get_by_default():
    with patch("lastfmcollagegenerator.network.requests.get") as mock_get:
        mock_get.return_value = make_response(200, b"data")
        fetcher = ResilientHttpFetcher(rate_limit=None)
        resp = fetcher.get("https://mock.cdn/art.png")
        assert resp.status_code == 200
        mock_get.assert_called_once()
