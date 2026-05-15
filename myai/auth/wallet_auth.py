"""
myai/auth/wallet_auth.py -- Wallet-based challenge-response auth for the MyAi SDK.

Replaces static API key auth with ETH private-key signing (EIP-191).

Dependencies:
    pip install httpx eth-account

Environment variables:
    AGENT_WALLET_KEY          -- 0x-prefixed ETH private key (preferred)
    MYAI_WALLET_PRIVATE_KEY   -- alias accepted by from_env()
    MYAI_API_KEY              -- legacy static key (deprecated, emits DeprecationWarning)
    MYAI_API_BASE             -- coordinator base URL
"""
from __future__ import annotations

import asyncio
import os
import time
import warnings
from typing import Optional

import httpx
from eth_account import Account
from eth_account.messages import encode_defunct


class WalletAuth:
    """
    Drop-in auth provider for MyAIClient.

    Performs SIWE/EIP-191 challenge-response against the coordinator and caches
    the resulting short-lived JWT, transparently refreshing it before expiry.

    Parameters
    ----------
    private_key:
        0x-prefixed Ethereum private key. Takes priority over api_key.
    coordinator_url:
        MyAi coordinator root URL (no trailing slash).
    api_key:
        Deprecated static API key accepted as a fallback while agents migrate
        to wallet auth.
    refresh_buffer_seconds:
        Re-authenticate this many seconds before expiry (default: 300).
    """

    DEFAULT_COORDINATOR_URL = "https://api.myaitoken.io"

    def __init__(
        self,
        private_key: Optional[str] = None,
        coordinator_url: str = DEFAULT_COORDINATOR_URL,
        *,
        api_key: Optional[str] = None,
        refresh_buffer_seconds: float = 300.0,
    ) -> None:
        if private_key is None and api_key is None:
            raise ValueError(
                "Provide private_key (ETH) or api_key (legacy). "
                "Set AGENT_WALLET_KEY or MYAI_API_KEY in the environment."
            )
        if api_key is not None and private_key is None:
            warnings.warn(
                "MyAi SDK: api_key/MYAI_API_KEY auth is deprecated. "
                "Set AGENT_WALLET_KEY or MYAI_WALLET_PRIVATE_KEY to use wallet auth.",
                DeprecationWarning,
                stacklevel=2,
            )

        self._private_key = private_key
        self._api_key = api_key
        self.coordinator_url = coordinator_url.rstrip("/")
        self._buffer = refresh_buffer_seconds

        self.address: Optional[str] = None
        if private_key:
            self.address = Account.from_key(private_key).address

        self._token: Optional[str] = None
        self._exp: float = 0.0
        self._lock: asyncio.Lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Class constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_env(cls, coordinator_url: Optional[str] = None) -> "WalletAuth":
        """
        Build from environment variables.

        Priority: AGENT_WALLET_KEY > MYAI_WALLET_PRIVATE_KEY > MYAI_API_KEY (deprecated).

        Raises
        ------
        EnvironmentError
            When no usable credential is found.
        """
        private_key = (
            os.environ.get("AGENT_WALLET_KEY")
            or os.environ.get("MYAI_WALLET_PRIVATE_KEY")
        )
        api_key = os.environ.get("MYAI_API_KEY") if not private_key else None
        base = coordinator_url or os.environ.get("MYAI_API_BASE", cls.DEFAULT_COORDINATOR_URL)

        if not private_key and not api_key:
            raise EnvironmentError(
                "Set AGENT_WALLET_KEY (preferred) or MYAI_API_KEY (deprecated) "
                "before using WalletAuth.from_env()."
            )
        return cls(private_key=private_key, coordinator_url=base, api_key=api_key)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def get_token(self) -> str:
        """Return a valid JWT, refreshing transparently when near expiry."""
        if self._private_key is None and self._api_key:
            return self._api_key  # legacy path -- no JWT

        async with self._lock:
            if self._token and time.time() < self._exp - self._buffer:
                return self._token
            return await self._refresh()

    async def headers(self) -> dict[str, str]:
        """Return {"Authorization": "Bearer <token>"} ready for httpx/aiohttp."""
        return {"Authorization": f"Bearer {await self.get_token()}"}

    def invalidate(self) -> None:
        """Force the next call to re-authenticate from scratch."""
        self._token = None
        self._exp = 0.0

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _refresh(self) -> str:
        if not self._private_key:
            raise RuntimeError("_refresh() requires a private key.")

        async with httpx.AsyncClient(timeout=30) as client:
            # 1. Get nonce / challenge
            r = await client.post(
                f"{self.coordinator_url}/auth/challenge",
                json={"wallet_address": self.address},
            )
            r.raise_for_status()
            challenge: str = r.json()["challenge"]

            # 2. Sign with EIP-191
            signable = encode_defunct(text=challenge)
            signed = Account.sign_message(signable, private_key=self._private_key)
            signature: str = signed.signature.hex()

            # 3. Submit, receive JWT
            r = await client.post(
                f"{self.coordinator_url}/auth/verify",
                json={
                    "wallet_address": self.address,
                    "challenge": challenge,
                    "signature": signature,
                },
            )
            r.raise_for_status()
            data = r.json()

        self._token = data["access_token"]
        self._exp = time.time() + int(data.get("expires_in", 3600))
        return self._token

    # ------------------------------------------------------------------
    # Async context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "WalletAuth":
        await self.get_token()
        return self

    async def __aexit__(self, *_: object) -> None:
        pass

    def __repr__(self) -> str:
        mode = "wallet" if self._private_key else "api-key (legacy)"
        return f"<WalletAuth mode={mode} address={self.address} url={self.coordinator_url!r}>"
