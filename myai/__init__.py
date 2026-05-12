from .client import MyAIClient
from .exceptions import InsufficientFundsError, NoProvidersError, PoCFailedError
from .openai_compat import MyAi, AsyncMyAi

__version__ = "2.1.0"
__all__ = [
    # OpenAI-compatible clients (recommended for new integrations)
    "MyAi",
    "AsyncMyAi",
    # Agentic commerce client (v2.0 Agent Developer Kit)
    "MyAIClient",
    # Exceptions
    "InsufficientFundsError",
    "NoProvidersError",
    "PoCFailedError",
]
