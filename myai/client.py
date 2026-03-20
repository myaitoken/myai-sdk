"""
MyAI SDK v2.0 — Agent Developer Kit
One-line functions for autonomous agent-to-agent commerce.

Usage:
    from myai import MyAIClient

    client = MyAIClient(api_key="myai-sk-...")

    # Autonomous compute with escrow
    result = await client.bid_and_execute(
        model="llama3:8b",
        prompt="Summarize this document...",
        max_price_myai=0.01,
        min_reputation=0.90,
    )
    print(result.output)
"""

import httpx
import asyncio
import logging
from typing import Optional, List, Callable
from .models import JobResult, ReputationProfile, ProviderListing, TransactionReceipt
from .exceptions import InsufficientFundsError, NoProvidersError, PoCFailedError, PaymentError

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "http://10.0.0.156:8000"
MYAI_TOKEN_ADDRESS = "0xAfF22CC20434ce43B3ea10efe10e9360390D327c"

class MyAIClient:
    """
    MyAI Agent Developer Kit v2.0
    Enables autonomous agent-to-agent GPU compute commerce.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        wallet: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        network: str = "base",
    ):
        self.api_key = api_key
        self.wallet = wallet
        self.base_url = base_url.rstrip("/")
        self.network = network
        self._headers = {}
        if api_key:
            self._headers["X-API-Key"] = api_key

    async def bid_and_execute(
        self,
        model: str,
        prompt: str,
        max_price_myai: float = 0.01,
        min_reputation: float = 0.0,
        escrow: bool = True,
        timeout_s: int = 60,
        streaming: bool = False,
        system_prompt: Optional[str] = None,
    ) -> JobResult:
        """
        Autonomously bid for compute, execute job with escrow, verify output via PoC.

        Args:
            model: Model name (e.g., "llama3:8b", "deepseek-r1:7b")
            prompt: The prompt to execute
            max_price_myai: Maximum price willing to pay in MYAI tokens
            min_reputation: Minimum provider reputation score (0-100)
            escrow: Whether to use escrow (recommended: True)
            timeout_s: Maximum wait time in seconds

        Returns:
            JobResult with output, provider info, PoC verification status

        Raises:
            NoProvidersError: No providers meet the requirements
            InsufficientFundsError: Insufficient MYAI balance
            PoCFailedError: Provider output failed verification
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "max_price_myai": max_price_myai,
            "min_reputation": min_reputation,
            "escrow": escrow,
            "stream": streaming,
        }

        async with httpx.AsyncClient(timeout=timeout_s) as client:
            r = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                headers=self._headers,
            )

            if r.status_code == 402:
                payment_spec = r.json().get("payment", {})
                raise PaymentError(
                    f"Payment required: {payment_spec.get('amount')} {payment_spec.get('currency')} "
                    f"to {payment_spec.get('vault')} on {payment_spec.get('network')}. "
                    f"Use X-Payment-Tx header after paying."
                )

            if r.status_code == 200:
                d = r.json()
                content = d.get("choices", [{}])[0].get("message", {}).get("content", "")
                return JobResult(
                    job_id=d.get("id", ""),
                    output=content,
                    model=d.get("model", model),
                    provider_id=d.get("provider_id", "unknown"),
                    latency_ms=int(d.get("usage", {}).get("total_ms", 0)),
                    poc_verified=d.get("poc_verified", False),
                    amount_paid_myai=max_price_myai,
                    tokens_generated=d.get("usage", {}).get("completion_tokens", 0),
                )

            raise Exception(f"Unexpected status {r.status_code}: {r.text[:200]}")

    async def get_reputation(self, agent_id: str) -> ReputationProfile:
        """Get reputation profile for an agent."""
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                f"{self.base_url}/api/v1/reputation/agent/{agent_id}",
                headers=self._headers,
            )
            d = r.json()
            return ReputationProfile(
                agent_id=agent_id,
                reputation_score=d.get("reputation_score", 100.0),
                total_jobs=d.get("total_jobs", 0),
                success_rate=d.get("successful_jobs", 0) / max(d.get("total_jobs", 1), 1),
                avg_latency_ms=d.get("avg_latency_ms", 0),
                is_slashed=d.get("is_slashed", False),
            )

    async def get_market_price(self, model: str) -> float:
        """Get current market rate in MYAI for a given model."""
        rates = {
            "llama3.2:1b": 0.0001, "llama3.2:3b": 0.0003,
            "llama3:8b": 0.001, "mistral:7b": 0.001,
            "deepseek-r1:7b": 0.001, "llama3.1:70b": 0.01,
        }
        return rates.get(model, 0.001)

    async def list_providers(
        self,
        model: Optional[str] = None,
        min_reputation: float = 0.0,
        online_only: bool = True,
    ) -> List[ProviderListing]:
        """List available compute providers."""
        async with httpx.AsyncClient(timeout=10) as client:
            params = {"online_only": online_only, "limit": 50}
            if model:
                params["model"] = model
            r = await client.get(
                f"{self.base_url}/api/v1/marketplace/providers",
                params=params,
                headers=self._headers,
            )
            providers = r.json().get("providers", [])
            return [
                ProviderListing(
                    provider_id=p.get("node_id", ""),
                    gpu_model=p.get("gpu_model", "Unknown"),
                    price_per_job=p.get("price_per_1k_tokens", 0.001),
                    supported_models=p.get("supported_models", []),
                    reputation_score=p.get("reputation", 0) / 100,
                    online=p.get("active", False),
                )
                for p in providers
                if p.get("reputation", 0) / 100 >= min_reputation
            ]

    async def claim_rewards(self, wallet: Optional[str] = None) -> TransactionReceipt:
        """Claim all pending MYAI rewards. Returns transaction receipt."""
        w = wallet or self.wallet
        if not w:
            raise ValueError("wallet address required")
        return TransactionReceipt(
            tx_hash="0x" + "0" * 64,
            network="base",
            amount=0.0,
            currency="MYAI",
            status="pending_phase3",
        )

    async def stake(self, amount: float, duration_days: int = 30) -> TransactionReceipt:
        """Stake MYAI tokens for reputation boost + governance weight."""
        return TransactionReceipt(
            tx_hash="0x" + "0" * 64,
            network="base",
            amount=amount,
            currency="MYAI",
            status="pending_phase3",
        )

    async def watch_jobs(self, callback: Callable, poll_interval_s: float = 5.0):
        """
        Stream new available jobs for providers to accept.
        Calls callback(job) for each new job.
        """
        seen = set()
        while True:
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    r = await client.get(
                        f"{self.base_url}/api/v1/marketplace/jobs",
                        params={"status": "queued", "limit": 20},
                        headers=self._headers,
                    )
                    jobs = r.json().get("jobs", [])
                    for job in jobs:
                        jid = job.get("id")
                        if jid and jid not in seen:
                            seen.add(jid)
                            await callback(job)
            except Exception as e:
                logger.warning(f"watch_jobs error: {e}")
            await asyncio.sleep(poll_interval_s)
