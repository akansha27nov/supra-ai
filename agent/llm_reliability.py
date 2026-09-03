# agent/llm_reliability.py
"""Shared retry + clean-failure handling for every LLM call in the app.
"""
from __future__ import annotations

import time
from typing import Callable, TypeVar

import openai

T = TypeVar("T")


class ExtractionFailedError(Exception):
    """Raised when an LLM call could not be completed after retries.

    Carries a short, user-facing reason (never a raw stack trace) so the API
    layer can surface a clean error instead of persisting bad/partial data as
    if it were a successful result.
    """

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


_RETRYABLE_EXCEPTIONS = (
    openai.RateLimitError,
    openai.APITimeoutError,
    openai.APIConnectionError,
    openai.InternalServerError,
)
_MAX_ATTEMPTS = 3
_BACKOFF_SECONDS = (1, 2, 4)  # wait before attempt 2, attempt 3, ...


def invoke_with_retry(call: Callable[[], T], *, step: str) -> T:
    """Invokes an LLM call with retries and clean failure handling."""
    last_error: Exception | None = None

    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            return call()
        except _RETRYABLE_EXCEPTIONS as e:
            last_error = e
            if attempt < _MAX_ATTEMPTS:
                time.sleep(_BACKOFF_SECONDS[attempt - 1])
                continue
            raise ExtractionFailedError(
                f"[{step}] The AI service is temporarily unavailable after "
                f"{_MAX_ATTEMPTS} attempts. Please try again in a moment. "
                f"({e.__class__.__name__})"
            ) from e
        except openai.AuthenticationError as e:
            # Not retryable — a config problem, not a traffic or document problem.
            raise ExtractionFailedError(
                f"[{step}] The AI service rejected the request (authentication error). "
                "This is a configuration issue, not a document problem — contact support."
            ) from e
        except openai.APIError as e:
            raise ExtractionFailedError(
                f"[{step}] The AI service returned an error and the request could not "
                f"be completed. Please try again in a moment. ({e.__class__.__name__})"
            ) from e
        except Exception as e:
            raise ExtractionFailedError(
                f"[{step}] Could not get a usable structured response. This can happen "
                "with scanned/image-only documents, non-English text, or corrupted "
                f"input. ({e.__class__.__name__})"
            ) from e

    # Unreachable, but keeps type-checkers happy.
    raise ExtractionFailedError(f"[{step}] Failed after retries. ({last_error})")
