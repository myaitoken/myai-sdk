# MyAI SDK v2.0

The Agent Developer Kit for the agentic economy. One-line functions for autonomous GPU compute.

## Install
```bash
pip install myai-sdk
```

## Quick Start
```python
from myai import MyAIClient

client = MyAIClient(api_key="myai-sk-...")

# Autonomous compute — bid, pay, execute, verify in one line
result = await client.bid_and_execute(
    model="llama3:8b",
    prompt="Analyze this smart contract for vulnerabilities...",
    max_price_myai=0.01,
    min_reputation=0.95,
    escrow=True,
)

print(result.output)
print(f"Paid: {result.amount_paid_myai} MYAI | PoC verified: {result.poc_verified}")
```

## LangChain Integration
```python
from myai.langchain_tool import MyAIComputeTool
tools = [MyAIComputeTool(api_key="myai-sk-...")]
# Any LangChain agent can now buy GPU compute autonomously
```

## Key Features
- **bid_and_execute()** — One-line autonomous compute with escrow and PoC
- **get_reputation()** — Query agent trust scores
- **list_providers()** — Discover available GPU compute nodes
- **watch_jobs()** — Real-time job stream for providers
- **claim_rewards()** — Claim MYAI token rewards (Phase 3)
- **stake()** — Stake for governance + reputation boost (Phase 3)

## MYAI Token
- Contract: `0xAfF22CC20434ce43B3ea10efe10e9360390D327c`
- Network: Base
