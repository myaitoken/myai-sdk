class MyAIError(Exception): pass
class InsufficientFundsError(MyAIError): pass
class NoProvidersError(MyAIError): pass
class PoCFailedError(MyAIError): pass
class PaymentError(MyAIError): pass
class TimeoutError(MyAIError): pass
