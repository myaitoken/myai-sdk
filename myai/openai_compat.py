"""
myai.openai_compat — OpenAI-compatible thin wrapper for the MyAi API.

Drop-in replacement for the openai Python SDK. Point base_url at
api.myaitoken.io and inject your MyAi key — everything else works
exactly as the openai SDK docs describe.

Usage
-----
    from myai.openai_compat import MyAi

    client = MyAi(api_key="myai_...")

    response = client.chat.completions.create(
        model="qwen2.5-14b-awq",
        messages=[{"role": "user", "content": "Hello!"}],
    )
    print(response.choices[0].message.content)

Environment variables
---------------------
    MYAI_API_KEY   -- API key (overrides constructor argument)
    MYAI_BASE_URL  -- Override API endpoint (default: https://api.myaitoken.io/v1)
"""

from __future__ import annotations

import os
from typing import Optional

try:
    import openai as _openai
except ImportError as exc:
    raise ImportError(
        "The openai package is required for myai.openai_compat.\n"
        "Install it with:  pip install 'myai-sdk[openai]'"
    ) from exc

__all__ = ["MyAi", "AsyncMyAi"]

_DEFAULT_BASE_URL = "https://api.myaitoken.io/v1"


class MyAi(_openai.OpenAI):
    """
    OpenAI-compatible MyAi client (sync).

    All methods (chat.completions, models, embeddings, ...) work exactly
    as the openai SDK -- we just override the base URL and inject the key.

    Parameters
    ----------
    api_key:
        Your MyAi API key (``myai_...``). Falls back to MYAI_API_KEY,
        then OPENAI_API_KEY environment variables.
    base_url:
        API endpoint. Defaults to https://api.myaitoken.io/v1 or MYAI_BASE_URL.
    **kwargs:
        Forwarded verbatim to openai.OpenAI (timeout, max_retries, ...).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs,
    ) -> None:
        resolved_key = (
            api_key
            or os.environ.get("MYAI_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
        )
        resolved_url = (
            base_url
            or os.environ.get("MYAI_BASE_URL")
            or _DEFAULT_BASE_URL
        )
        super().__init__(api_key=resolved_key, base_url=resolved_url, **kwargs)


class AsyncMyAi(_openai.AsyncOpenAI):
    """
    Async OpenAI-compatible MyAi client. Use with await / async for.

    Parameters
    ----------
    api_key, base_url, **kwargs:
        Same as MyAi.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs,
    ) -> None:
        resolved_key = (
            api_key
            or os.environ.get("MYAI_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
        )
        resolved_url = (
            base_url
            or os.environ.get("MYAI_BASE_URL")
            or _DEFAULT_BASE_URL
        )
        super().__init__(api_key=resolved_key, base_url=resolved_url, **kwargs)
