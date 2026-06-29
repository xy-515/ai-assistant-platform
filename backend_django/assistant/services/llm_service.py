"""
Generic LLM Service — OpenAI-compatible API with retry, timeout, and streaming.

Usage:
    from assistant.services.llm_service import chat_with_llm, stream_with_llm

    # Sync (non-streaming)
    reply = chat_with_llm("You are helpful.", "Hello!")

    # Async streaming
    async for chunk in stream_with_llm("You are helpful.", "Hello!"):
        yield chunk
"""

import asyncio
import logging
import time
from typing import AsyncGenerator

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)

# ── Config helpers (read dynamically from settings) ─────

def _cfg(name, default=None):
    return getattr(settings, name, default)


# ── Core Client ─────────────────────────────────────────

def _build_client() -> httpx.AsyncClient:
    """Build an httpx client with auth headers."""
    return httpx.AsyncClient(
        base_url=_cfg("LLM_BASE_URL", "https://api.deepseek.com"),
        headers={
            "Authorization": f"Bearer {_cfg('LLM_API_KEY', '')}",
            "Content-Type": "application/json",
        },
        timeout=httpx.Timeout(_cfg("LLM_TIMEOUT", 60)),
    )


# ── Retry Logic ─────────────────────────────────────────

async def _retry_request(
    request_fn,
    max_retries: int | None = None,
    delay: float | None = None,
):
    if max_retries is None:
        max_retries = _cfg("LLM_MAX_RETRIES", 3)
    if delay is None:
        delay = _cfg("LLM_RETRY_DELAY", 1.0)
    """Execute a request with exponential backoff retry.

    Retries on: network errors, 429 (rate limit), 5xx server errors.
    Returns whatever request_fn returns (httpx.Response or tuple).
    """
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            result = await request_fn()

            # Unwrap: request_fn may return (response, client) or just response
            if isinstance(result, tuple):
                response = result[0]
            else:
                response = result

            # Success or client error (don't retry 4xx except 429)
            if response.status_code < 500 and response.status_code != 429:
                return result  # Return original (tuple or response)

            # Rate limit — wait and retry
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After", str(delay * (2 ** attempt)))
                wait = float(retry_after) if retry_after.replace('.','').isdigit() else delay * (2 ** attempt)
                logger.warning("LLM rate limited (429). Waiting %.1fs (attempt %d/%d)",
                               wait, attempt + 1, max_retries)
                await asyncio.sleep(wait)
                continue

            # Server error — retry
            logger.warning("LLM server error %d (attempt %d/%d)",
                           response.status_code, attempt + 1, max_retries)
            await asyncio.sleep(delay * (2 ** attempt))
            last_error = RuntimeError(
                f"LLM API returned {response.status_code}: {response.text[:200]}")

        except (httpx.TimeoutException, httpx.ConnectError,
                httpx.ReadError, httpx.RemoteProtocolError) as e:
            logger.warning("LLM network error (attempt %d/%d): %s",
                           attempt + 1, max_retries, str(e)[:100])
            await asyncio.sleep(delay * (2 ** attempt))
            last_error = e

    raise last_error or RuntimeError("LLM request failed after max retries")


# ── Streaming Parser (SSE) ─────────────────────────────

async def _parse_stream(response: httpx.Response) -> AsyncGenerator[str, None]:
    """Parse Server-Sent Events (SSE) from OpenAI-compatible streaming API."""
    async for line in response.aiter_lines():
        if not line or not line.startswith("data: "):
            continue
        data = line[6:]  # strip "data: "
        if data == "[DONE]":
            break
        import json
        try:
            obj = json.loads(data)
            delta = obj.get("choices", [{}])[0].get("delta", {})
            content = delta.get("content", "")
            if content:
                yield content
        except (json.JSONDecodeError, KeyError, IndexError):
            continue


# ── Public API ──────────────────────────────────────────

async def chat_with_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
    *,
    model: str | None = None,
    max_tokens: int | None = None,
    extra_messages: list[dict] | None = None,
) -> str:
    """Call LLM (non-streaming) and return the full response.

    Args:
        system_prompt: System role message.
        user_prompt: User role message.
        temperature: 0.0-2.0, lower = more deterministic.
        model: Override default model.
        max_tokens: Override default max tokens.
        extra_messages: Additional messages inserted between system and user.
            Format: [{"role":"assistant","content":"..."}, {"role":"user","content":"..."}]

    Returns:
        Full response text from the LLM.

    Raises:
        RuntimeError: After max retries exhausted.
        ValueError: If API key is not configured.
    """
    if not _cfg("LLM_API_KEY"):
        raise ValueError("LLM_API_KEY not configured in Django settings")

    messages = [{"role": "system", "content": system_prompt}]
    if extra_messages:
        messages.extend(extra_messages)
    messages.append({"role": "user", "content": user_prompt})

    payload = {
        "model": model or _cfg("LLM_MODEL_NAME", "deepseek-chat"),
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens or _cfg("LLM_MAX_TOKENS", 4096),
        "stream": False,
    }

    async def _request():
        client = _build_client()
        try:
            return await client.post("/v1/chat/completions", json=payload)
        finally:
            await client.aclose()

    response = await _retry_request(_request)
    if response.status_code >= 400:
        raise RuntimeError(
            f"LLM API error {response.status_code}: {response.text[:300]}"
        )
    data = response.json()
    return data["choices"][0]["message"]["content"]


async def stream_with_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
    *,
    model: str | None = None,
    max_tokens: int | None = None,
    extra_messages: list[dict] | None = None,
) -> AsyncGenerator[str, None]:
    """Call LLM with streaming output.

    Each yielded value is a text chunk (typically a few characters or a word).

    Usage:
        async for chunk in stream_with_llm("You are helpful.", "Hello!"):
            print(chunk, end="", flush=True)
    """
    if not _cfg("LLM_API_KEY"):
        raise ValueError("LLM_API_KEY not configured in Django settings")

    messages = [{"role": "system", "content": system_prompt}]
    if extra_messages:
        messages.extend(extra_messages)
    messages.append({"role": "user", "content": user_prompt})

    payload = {
        "model": model or _cfg("LLM_MODEL_NAME", "deepseek-chat"),
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens or _cfg("LLM_MAX_TOKENS", 4096),
        "stream": True,
    }

    async def _request():
        client = _build_client()
        # Don't close client here — stream parser needs it
        return await client.post("/v1/chat/completions", json=payload), client

    response, client = await _retry_request(_request)
    if response.status_code >= 400:
        await client.aclose()
        raise RuntimeError(
            f"LLM API error {response.status_code}: {response.text[:300]}"
        )
    try:
        async for chunk in _parse_stream(response):
            yield chunk
    finally:
        await client.aclose()


# ── Sync Wrapper (for Django views that aren't async) ──

def chat_with_llm_sync(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
    **kwargs,
) -> str:
    """Synchronous wrapper around chat_with_llm.

    Use this in regular Django views or anywhere async is inconvenient.
    """
    return asyncio.run(chat_with_llm(system_prompt, user_prompt, temperature, **kwargs))
