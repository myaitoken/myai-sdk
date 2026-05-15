from .client import MyAIClient
from .auth.wallet_auth import WalletAuth
from .exceptions import InsufficientFundsError, NoProvidersError, PoCFailedError
from .openai_compat import MyAi, AsyncMyAi

__version__ = "2.2.0"
__all__ = [
    # OpenAI-compatible
    "MyAi", "AsyncMyAi",
    # Agentic commerce
    "MyAIClient",
    # Wallet auth (v2.2)
    "WalletAuth",
    # Exceptions
    "InsufficientFundsError", "NoProvidersError", "PoCFailedError",
]
