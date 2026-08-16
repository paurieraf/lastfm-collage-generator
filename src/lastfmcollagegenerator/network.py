import random
import threading
import time
import urllib.parse
from typing import Any, Callable, Dict, Optional

import requests

DEFAULT_RATE_LIMIT = 5.0
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_BASE_DELAY = 0.5
DEFAULT_MAX_DELAY = 8.0
DEFAULT_FAILURE_THRESHOLD = 5
DEFAULT_COOLDOWN_SECONDS = 60.0

_TRANSIENT_STATUS_CODES = (429,)


class FetchError(requests.RequestException):
    """Raised when an artwork download fails after all retry attempts."""


class CircuitOpenError(FetchError):
    """Raised when the circuit breaker for a host is open."""


class TokenBucket:
    """Thread-safe token-bucket rate limiter with a blocking acquire."""

    def __init__(
        self, rate: float = DEFAULT_RATE_LIMIT, capacity: Optional[float] = None
    ) -> None:
        self.rate = float(rate)
        self.capacity = float(capacity if capacity is not None else rate)
        self._tokens = self.capacity
        self._updated = time.monotonic()
        self._condition = threading.Condition()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._updated
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
        self._updated = now

    def acquire(self) -> None:
        with self._condition:
            while True:
                self._refill()
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return
                needed = 1.0 - self._tokens
                wait_seconds = needed / self.rate
                self._condition.wait(timeout=wait_seconds)


class CircuitBreaker:
    """Per-host circuit breaker with closed / open / half-open states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

    def __init__(
        self,
        failure_threshold: int = DEFAULT_FAILURE_THRESHOLD,
        cooldown_seconds: float = DEFAULT_COOLDOWN_SECONDS,
    ) -> None:
        self.failure_threshold = int(failure_threshold)
        self.cooldown_seconds = float(cooldown_seconds)
        self._state = self.CLOSED
        self._failures = 0
        self._opened_at: Optional[float] = None
        self._lock = threading.Lock()

    @property
    def state(self) -> str:
        with self._lock:
            return self._state

    def allow_request(self) -> bool:
        with self._lock:
            if self._state == self.OPEN:
                now = time.monotonic()
                if self._opened_at is not None and (
                    now - self._opened_at >= self.cooldown_seconds
                ):
                    self._state = self.HALF_OPEN
                else:
                    return False
            return True

    def record_success(self) -> None:
        with self._lock:
            self._failures = 0
            self._state = self.CLOSED

    def record_failure(self) -> None:
        with self._lock:
            if self._state == self.HALF_OPEN:
                self._state = self.OPEN
                self._opened_at = time.monotonic()
                return
            self._failures += 1
            if self._failures >= self.failure_threshold:
                self._state = self.OPEN
                self._opened_at = time.monotonic()


def retry_with_full_jitter(
    fn: Callable[[], Any],
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    base_delay: float = DEFAULT_BASE_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> Any:
    """Retry a callable on transient failures with exponential backoff and jitter.

    ``fn`` must either return a ``requests.Response`` or raise a
    ``requests.RequestException`` / ``OSError``. Responses with status 429
    or 5xx are treated as transient failures and retried.
    """
    last_exc: Optional[BaseException] = None
    for attempt in range(max_attempts):
        try:
            resp = fn()
        except (requests.RequestException, OSError) as exc:
            last_exc = exc
        else:
            status = getattr(resp, "status_code", None)
            if status in _TRANSIENT_STATUS_CODES or (
                isinstance(status, int) and status >= 500
            ):
                last_exc = FetchError("HTTP {0}".format(status))
            else:
                return resp

        if attempt + 1 < max_attempts:
            delay = min(max_delay, base_delay * (2**attempt))
            sleep_fn(random.uniform(0, delay))

    raise FetchError(
        "Request failed after {0} attempts".format(max_attempts)
    ) from last_exc


class ResilientHttpFetcher:
    """Composes rate limiting, circuit breaking and retry logic around requests.get."""

    def __init__(
        self,
        rate_limit: Optional[float] = DEFAULT_RATE_LIMIT,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        base_delay: float = DEFAULT_BASE_DELAY,
        max_delay: float = DEFAULT_MAX_DELAY,
        failure_threshold: int = DEFAULT_FAILURE_THRESHOLD,
        cooldown_seconds: float = DEFAULT_COOLDOWN_SECONDS,
        sleep_fn: Callable[[float], None] = time.sleep,
        request_fn: Optional[Callable[..., Any]] = None,
    ) -> None:
        self.max_attempts = max(1, int(max_attempts))
        self.base_delay = float(base_delay)
        self.max_delay = float(max_delay)
        self.failure_threshold = int(failure_threshold)
        self.cooldown_seconds = float(cooldown_seconds)
        self.sleep_fn = sleep_fn
        self.request_fn = request_fn
        self.rate_limiter: Optional[TokenBucket] = None
        if rate_limit is not None and float(rate_limit) > 0:
            self.rate_limiter = TokenBucket(rate=float(rate_limit))
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._breakers_lock = threading.Lock()

    def _breaker_for(self, host: str) -> CircuitBreaker:
        with self._breakers_lock:
            breaker = self._breakers.get(host)
            if breaker is None:
                breaker = CircuitBreaker(
                    failure_threshold=self.failure_threshold,
                    cooldown_seconds=self.cooldown_seconds,
                )
                self._breakers[host] = breaker
            return breaker

    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[Any] = None,
    ) -> Any:
        host = urllib.parse.urlparse(url).netloc or url
        breaker = self._breaker_for(host)

        if not breaker.allow_request():
            raise CircuitOpenError("Circuit open for host: {0}".format(host))

        last_exc: Optional[BaseException] = None
        for attempt in range(self.max_attempts):
            if self.rate_limiter is not None:
                self.rate_limiter.acquire()

            try:
                if self.request_fn is not None:
                    request_fn = self.request_fn
                else:
                    request_fn = requests.get
                resp = request_fn(url, headers=headers, timeout=timeout)
            except (requests.RequestException, OSError) as exc:
                breaker.record_failure()
                last_exc = exc
            else:
                status = resp.status_code
                if status in _TRANSIENT_STATUS_CODES or status >= 500:
                    breaker.record_failure()
                    last_exc = FetchError("HTTP {0}".format(status))
                else:
                    breaker.record_success()
                    return resp

            if breaker.state == CircuitBreaker.OPEN:
                break

            if attempt + 1 < self.max_attempts:
                delay = min(self.max_delay, self.base_delay * (2**attempt))
                self.sleep_fn(random.uniform(0, delay))

        raise FetchError(
            "Request failed for {0} after {1} attempts".format(host, attempt + 1)
        ) from last_exc
