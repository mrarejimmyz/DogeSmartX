"""
DogeSmartX Exceptions Module

Custom exception classes for DogeSmartX agent with detailed error handling
and debugging capabilities.
"""

from typing import Optional, Dict, Any


class DogeSmartXError(Exception):
    """Base exception for DogeSmartX agent."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/debugging."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context
        }
    
    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"


class SwapError(DogeSmartXError):
    """Exceptions related to swap operations."""
    
    def __init__(self, message: str, swap_id: Optional[str] = None, 
                 direction: Optional[str] = None, amount: Optional[float] = None,
                 **kwargs):
        context = {
            "swap_id": swap_id,
            "direction": direction,
            "amount": amount
        }
        context.update(kwargs)
        super().__init__(message, "SWAP_ERROR", context)


class ContractError(DogeSmartXError):
    """Exceptions related to smart contract operations."""
    
    def __init__(self, message: str, contract_name: Optional[str] = None,
                 contract_address: Optional[str] = None, function_name: Optional[str] = None,
                 **kwargs):
        context = {
            "contract_name": contract_name,
            "contract_address": contract_address,
            "function_name": function_name
        }
        context.update(kwargs)
        super().__init__(message, "CONTRACT_ERROR", context)


class NetworkError(DogeSmartXError):
    """Exceptions related to network operations."""
    
    def __init__(self, message: str, network: Optional[str] = None,
                 rpc_url: Optional[str] = None, **kwargs):
        context = {
            "network": network,
            "rpc_url": rpc_url
        }
        context.update(kwargs)
        super().__init__(message, "NETWORK_ERROR", context)


class ValidationError(DogeSmartXError):
    """Exceptions related to data validation."""
    
    def __init__(self, message: str, field: Optional[str] = None,
                 value: Optional[Any] = None, **kwargs):
        context = {
            "field": field,
            "value": value
        }
        context.update(kwargs)
        super().__init__(message, "VALIDATION_ERROR", context)


class MarketDataError(DogeSmartXError):
    """Exceptions related to market data operations."""
    
    def __init__(self, message: str, symbol: Optional[str] = None,
                 provider: Optional[str] = None, **kwargs):
        context = {
            "symbol": symbol,
            "provider": provider
        }
        context.update(kwargs)
        super().__init__(message, "MARKET_DATA_ERROR", context)


class TimeoutError(DogeSmartXError):
    """Exceptions related to timeout operations."""
    
    def __init__(self, message: str, operation: Optional[str] = None,
                 timeout_seconds: Optional[float] = None, **kwargs):
        context = {
            "operation": operation,
            "timeout_seconds": timeout_seconds
        }
        context.update(kwargs)
        super().__init__(message, "TIMEOUT_ERROR", context)


class InsufficientFundsError(SwapError):
    """Exception for insufficient funds during swap."""
    
    def __init__(self, required_amount: float, available_amount: float,
                 token: str, **kwargs):
        message = f"Insufficient {token}: required {required_amount}, available {available_amount}"
        context = {
            "required_amount": required_amount,
            "available_amount": available_amount,
            "token": token
        }
        context.update(kwargs)
        super().__init__(message, error_code="INSUFFICIENT_FUNDS", **context)


class InvalidSwapDirectionError(SwapError):
    """Exception for invalid swap direction."""
    
    def __init__(self, direction: str, **kwargs):
        message = f"Invalid swap direction: {direction}. Use 'eth_to_doge' or 'doge_to_eth'"
        super().__init__(message, direction=direction, error_code="INVALID_DIRECTION", **kwargs)


class ContractNotDeployedError(ContractError):
    """Exception for undeployed contracts."""
    
    def __init__(self, contract_name: str, **kwargs):
        message = f"Contract '{contract_name}' not deployed. Deploy contract first."
        super().__init__(message, contract_name=contract_name, 
                        error_code="CONTRACT_NOT_DEPLOYED", **kwargs)


class HashlockMismatchError(SwapError):
    """Exception for hashlock verification failures."""
    
    def __init__(self, expected_hash: str, provided_hash: str, **kwargs):
        message = f"Hashlock mismatch: expected {expected_hash[:16]}..., got {provided_hash[:16]}..."
        context = {
            "expected_hash": expected_hash,
            "provided_hash": provided_hash
        }
        context.update(kwargs)
        super().__init__(message, error_code="HASHLOCK_MISMATCH", **context)


class TimelockExpiredError(SwapError):
    """Exception for expired timelock."""
    
    def __init__(self, swap_id: str, expiry_time: int, current_time: int, **kwargs):
        message = f"Timelock expired for swap {swap_id}. Refund available."
        context = {
            "expiry_time": expiry_time,
            "current_time": current_time,
            "expired_hours": (current_time - expiry_time) / 3600
        }
        context.update(kwargs)
        super().__init__(message, swap_id=swap_id, error_code="TIMELOCK_EXPIRED", **context)


class PartialFillError(SwapError):
    """Exception for partial fill operations."""
    
    def __init__(self, message: str, swap_id: str, requested_amount: float,
                 available_amount: float, **kwargs):
        context = {
            "requested_amount": requested_amount,
            "available_amount": available_amount
        }
        context.update(kwargs)
        super().__init__(message, swap_id=swap_id, error_code="PARTIAL_FILL_ERROR", **context)


# Exception handling utilities
def handle_exception(func):
    """Decorator for standardized exception handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DogeSmartXError:
            # Re-raise DogeSmartX exceptions as-is
            raise
        except Exception as e:
            # Wrap other exceptions in DogeSmartXError
            context = {
                "function": func.__name__,
                "args": str(args),
                "kwargs": str(kwargs),
                "original_error": str(e),
                "original_type": type(e).__name__
            }
            raise DogeSmartXError(
                f"Unexpected error in {func.__name__}: {str(e)}",
                error_code="UNEXPECTED_ERROR",
                context=context
            ) from e
    return wrapper


def log_exception(logger, exception: DogeSmartXError) -> None:
    """Log exception with full context for debugging."""
    error_dict = exception.to_dict()
    logger.error(
        f"DogeSmartX Error: {error_dict['message']}", 
        extra={
            "error_code": error_dict["error_code"],
            "error_type": error_dict["error_type"],
            "context": error_dict["context"]
        }
    )
