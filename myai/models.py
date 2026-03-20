from dataclasses import dataclass
from typing import Optional, List

@dataclass
class JobResult:
    job_id: str
    output: str
    model: str
    provider_id: str
    latency_ms: int
    poc_verified: bool
    amount_paid_myai: float
    tokens_generated: int

@dataclass
class ReputationProfile:
    agent_id: str
    reputation_score: float
    total_jobs: int
    success_rate: float
    avg_latency_ms: float
    is_slashed: bool

@dataclass
class ProviderListing:
    provider_id: str
    gpu_model: str
    price_per_job: float
    supported_models: List[str]
    reputation_score: float
    online: bool

@dataclass
class TransactionReceipt:
    tx_hash: str
    network: str
    amount: float
    currency: str
    status: str
