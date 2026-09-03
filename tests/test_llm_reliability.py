import httpx
import openai
import pytest

from agent.llm_reliability import ExtractionFailedError, invoke_with_retry


def _timeout_error():
    return openai.APITimeoutError(request=httpx.Request("POST", "https://api.openai.com/v1/x"))


def _connection_error():
    return openai.APIConnectionError(request=httpx.Request("POST", "https://api.openai.com/v1/x"))


def _auth_error():
    response = httpx.Response(401, request=httpx.Request("POST", "https://api.openai.com/v1/x"))
    return openai.AuthenticationError("bad key", response=response, body=None)


def test_succeeds_on_first_attempt_without_retrying(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)
    calls = {"n": 0}

    def call():
        calls["n"] += 1
        return "ok"

    assert invoke_with_retry(call, step="test") == "ok"
    assert calls["n"] == 1


def test_retries_transient_error_then_succeeds(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)
    calls = {"n": 0}

    def call():
        calls["n"] += 1
        if calls["n"] < 3:
            raise _timeout_error()
        return "recovered"

    result = invoke_with_retry(call, step="test")

    assert result == "recovered"
    assert calls["n"] == 3  # failed twice, succeeded on the 3rd (final) attempt


def test_raises_clean_error_after_exhausting_retries(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)
    calls = {"n": 0}

    def call():
        calls["n"] += 1
        raise _connection_error()

    with pytest.raises(ExtractionFailedError) as exc_info:
        invoke_with_retry(call, step="extract")

    assert calls["n"] == 3  # stopped after _MAX_ATTEMPTS, didn't retry forever
    assert "temporarily unavailable" in exc_info.value.reason
    assert "[extract]" in exc_info.value.reason


def test_authentication_error_is_not_retried(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)
    calls = {"n": 0}

    def call():
        calls["n"] += 1
        raise _auth_error()

    with pytest.raises(ExtractionFailedError) as exc_info:
        invoke_with_retry(call, step="extract")

    assert calls["n"] == 1  # no retry — a bad key won't fix itself
    assert "authentication error" in exc_info.value.reason


def test_non_openai_error_is_not_retried_and_surfaces_clean_message(monkeypatch):
    # Simulates a structured-output validation failure — e.g. the model's
    # response didn't match the expected schema because the input document
    # was a low-quality scan or non-English text.
    monkeypatch.setattr("time.sleep", lambda s: None)
    calls = {"n": 0}

    def call():
        calls["n"] += 1
        raise ValueError("could not parse model output into schema")

    with pytest.raises(ExtractionFailedError) as exc_info:
        invoke_with_retry(call, step="extract")

    assert calls["n"] == 1  # not retried — garbled input won't parse better on attempt 2
    assert "scanned/image-only" in exc_info.value.reason
    assert "non-English" in exc_info.value.reason
