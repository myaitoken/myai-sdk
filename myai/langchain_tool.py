"""
MyAI LangChain Tool — plug any LangChain agent into MyAI compute.

Usage:
    from myai.langchain_tool import MyAIComputeTool
    from langchain.agents import AgentExecutor

    tools = [MyAIComputeTool(api_key="myai-sk-...")]
    # Now any LangChain agent can autonomously buy GPU compute from MyAI
"""
try:
    from langchain.tools import BaseTool
    from pydantic import BaseModel, Field

    class MyAIInput(BaseModel):
        model: str = Field(description="Model name: llama3:8b, deepseek-r1:7b, etc.")
        prompt: str = Field(description="The prompt to run on GPU compute")
        max_price_myai: float = Field(default=0.01, description="Max MYAI tokens to pay")

    class MyAIComputeTool(BaseTool):
        name = "myai_compute"
        description = (
            "Run a prompt on distributed GPU compute via MyAI marketplace. "
            "Automatically handles payment, escrow, and proof-of-compute verification. "
            "Use for any compute-intensive AI tasks."
        )
        args_schema = MyAIInput
        api_key: str = ""

        def _run(self, model: str, prompt: str, max_price_myai: float = 0.01) -> str:
            import asyncio
            from myai import MyAIClient
            client = MyAIClient(api_key=self.api_key)
            result = asyncio.run(client.bid_and_execute(model=model, prompt=prompt, max_price_myai=max_price_myai))
            return result.output

        async def _arun(self, model: str, prompt: str, max_price_myai: float = 0.01) -> str:
            from myai import MyAIClient
            client = MyAIClient(api_key=self.api_key)
            result = await client.bid_and_execute(model=model, prompt=prompt, max_price_myai=max_price_myai)
            return result.output

except ImportError:
    class MyAIComputeTool:
        def __init__(self, **kwargs):
            raise ImportError("Install langchain: pip install langchain")
