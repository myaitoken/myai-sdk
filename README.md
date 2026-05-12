# MyAI Python SDK

OpenAI-compatible Python client for the [MyAi](https://myaitoken.io) decentralized compute network.

## Install

```bash
pip install 'myai-sdk[openai]'
```

## Quick Start — 5 lines

```python
from myai import MyAi

client = MyAi(api_key="myai_...")  # or set MYAI_API_KEY env var

response = client.chat.completions.create(
    model="qwen2.5-14b-awq",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)
```

That's it. Any code that uses the `openai` Python SDK works with `MyAi` — just swap the import.

## Models

```python
for model in client.models.list():
    print(model.id)
```

## Embeddings

```python
result = client.embeddings.create(
    model="nomic-embed-text",
    input="The quick brown fox",
)
print(result.data[0].embedding[:5])
```

## Streaming

```python
with client.chat.completions.create(
    model="qwen2.5-14b-awq",
    messages=[{"role": "user", "content": "Count to 5"}],
    stream=True,
) as stream:
    for chunk in stream:
        print(chunk.choices[0].delta.content or "", end="", flush=True)
```

## Async

```python
from myai import AsyncMyAi

client = AsyncMyAi(api_key="myai_...")

async def main():
    response = await client.chat.completions.create(
        model="qwen2.5-14b-awq",
        messages=[{"role": "user", "content": "Hello async!"}],
    )
    print(response.choices[0].message.content)
```

## Environment Variables

| Variable | Description |
|---|---|
| `MYAI_API_KEY` | Your MyAi API key |
| `MYAI_BASE_URL` | Override endpoint (default: `https://api.myaitoken.io/v1`) |

## Agent Developer Kit (v2.0)

For autonomous agent-to-agent compute with escrow and Proof-of-Compute:

```python
from myai import MyAIClient

client = MyAIClient(api_key="myai_...")

result = await client.bid_and_execute(
    model="llama3:8b",
    prompt="Analyze this contract...",
    max_price_myai=0.01,
    min_reputation=0.95,
    escrow=True,
)
print(result.output)
print(f"Paid: {result.amount_paid_myai} MYAI | PoC: {result.poc_verified}")
```

## LangChain

```python
from myai.langchain_tool import MyAIComputeTool

tools = [MyAIComputeTool(api_key="myai_...")]
# Any LangChain agent can now buy GPU compute autonomously
```

## Links

- [myaitoken.io](https://myaitoken.io)
- [API Reference](https://myaitoken.io/docs)
- [MYAI Token](https://basescan.org/address/0xAfF22CC20434ce43B3ea10efe10e9360390D327c) — Base network
