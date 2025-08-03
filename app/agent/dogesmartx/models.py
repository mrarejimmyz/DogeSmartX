"""
DogeSmartX Data Models

Pydantic models for type safety, validation, and serialization in DogeSmartX agent.
"""

import time
from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator
from decimal import Decimal


class SwapStatus(str, Enum):
    """Enumeration of swap statuses."""
    PENDING = "pending"
    PARTIALLY_FILLED = "partially_filled"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class SwapDirection(str, Enum):
    """Enumeration of swap directions."""
    ETH_TO_DOGE = "eth_to_doge"
    DOGE_TO_ETH = "doge_to_eth"


class NetworkType(str, Enum):
    """Enumeration of supported networks."""
    ETHEREUM = "ethereum"
    DOGECOIN = "dogecoin"


class ChainConfig(BaseModel):
    """Configuration for a blockchain network."""
    name: str
    network_type: NetworkType
    rpc_url: str
    chain_id: Optional[int] = None
    min_confirmations: int = Field(default=3, ge=1)
    gas_limit: Optional[int] = Field(default=300000, ge=21000)
    gas_price_gwei: Optional[float] = Field(default=50.0, ge=0)
    
    @validator('rpc_url')
    def validate_rpc_url(cls, v):
        if not v or not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('RPC URL must be a valid HTTP/HTTPS URL')
        return v


class MarketData(BaseModel):
    """Market data for trading pairs."""
    symbol: str
    price_usd: Decimal = Field(..., ge=0)
    price_change_24h: Optional[Decimal] = None
    volume_24h: Optional[Decimal] = None
    market_cap: Optional[Decimal] = None
    timestamp: float = Field(default_factory=time.time)
    source: Optional[str] = None
    
    @validator('price_usd', 'price_change_24h', 'volume_24h', 'market_cap', pre=True)
    def convert_to_decimal(cls, v):
        if v is None:
            return v
        return Decimal(str(v))
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }


class GasFees(BaseModel):
    """Current gas fee information."""
    slow: Decimal = Field(..., ge=0)
    standard: Decimal = Field(..., ge=0)
    fast: Decimal = Field(..., ge=0)
    instant: Decimal = Field(..., ge=0)
    timestamp: float = Field(default_factory=time.time)
    network: str = "ethereum"
    
    @validator('slow', 'standard', 'fast', 'instant', pre=True)
    def convert_to_decimal(cls, v):
        return Decimal(str(v))
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class SwapOrder(BaseModel):
    """A cross-chain swap order."""
    swap_id: str
    direction: SwapDirection
    from_chain: NetworkType
    to_chain: NetworkType
    from_token: str
    to_token: str
    amount: Decimal = Field(..., gt=0)
    filled_amount: Decimal = Field(default=Decimal("0"), ge=0)
    status: SwapStatus = SwapStatus.PENDING
    
    # Security features
    secret_hash: str
    timelock_expiry: int = Field(..., gt=0)
    partial_fills_enabled: bool = True
    
    # Timestamps
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    completed_at: Optional[float] = None
    
    # Optional fields
    exchange_rate: Optional[Decimal] = None
    slippage_tolerance: Decimal = Field(default=Decimal("0.5"), ge=0, le=100)
    charity_contribution: Decimal = Field(default=Decimal("0"), ge=0)
    gas_estimate: Optional[Dict[str, Any]] = None
    
    @validator('amount', 'filled_amount', 'slippage_tolerance', 'charity_contribution', pre=True)
    def convert_to_decimal(cls, v):
        return Decimal(str(v))
    
    @validator('filled_amount')
    def validate_filled_amount(cls, v, values):
        if 'amount' in values and v > values['amount']:
            raise ValueError('Filled amount cannot exceed total amount')
        return v
    
    @validator('timelock_expiry')
    def validate_timelock_expiry(cls, v):
        current_time = int(time.time())
        if v <= current_time:
            raise ValueError('Timelock expiry must be in the future')
        return v
    
    @property
    def remaining_amount(self) -> Decimal:
        """Calculate remaining amount to be filled."""
        return self.amount - self.filled_amount
    
    @property
    def fill_percentage(self) -> float:
        """Calculate fill percentage."""
        if self.amount == 0:
            return 0.0
        return float((self.filled_amount / self.amount) * 100)
    
    @property
    def is_expired(self) -> bool:
        """Check if timelock has expired."""
        return int(time.time()) >= self.timelock_expiry
    
    @property
    def time_remaining_hours(self) -> float:
        """Calculate hours remaining until timelock expiry."""
        time_remaining = self.timelock_expiry - int(time.time())
        return max(0.0, time_remaining / 3600)
    
    def update_status(self) -> None:
        """Update status based on current state."""
        if self.is_expired and self.status not in [SwapStatus.COMPLETED, SwapStatus.CANCELLED]:
            self.status = SwapStatus.EXPIRED
        elif self.filled_amount >= self.amount:
            self.status = SwapStatus.COMPLETED
            self.completed_at = time.time()
        elif self.filled_amount > 0:
            self.status = SwapStatus.PARTIALLY_FILLED
        
        self.updated_at = time.time()
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class PartialFill(BaseModel):
    """A partial fill for a swap order."""
    fill_id: str
    swap_id: str
    amount: Decimal = Field(..., gt=0)
    price: Optional[Decimal] = None
    timestamp: float = Field(default_factory=time.time)
    transaction_hash: Optional[str] = None
    block_number: Optional[int] = None
    
    @validator('amount', 'price', pre=True)
    def convert_to_decimal(cls, v):
        if v is None:
            return v
        return Decimal(str(v))
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }


class ContractDeployment(BaseModel):
    """Smart contract deployment information."""
    contract_name: str
    network: NetworkType
    address: str
    deployment_block: int
    deployment_hash: str
    abi_hash: Optional[str] = None
    verified: bool = False
    deployment_time: float = Field(default_factory=time.time)
    
    @validator('address')
    def validate_address(cls, v):
        if not v or v == "0x" or len(v) != 42:
            raise ValueError('Invalid contract address')
        return v.lower()


class TradingSession(BaseModel):
    """Trading session statistics."""
    session_id: str
    start_time: float = Field(default_factory=time.time)
    end_time: Optional[float] = None
    
    # Statistics
    total_swaps: int = 0
    completed_swaps: int = 0
    failed_swaps: int = 0
    partial_fills: int = 0
    total_volume_usd: Decimal = Field(default=Decimal("0"))
    charity_contributions: Decimal = Field(default=Decimal("0"))
    
    # Performance metrics
    average_completion_time: Optional[float] = None
    success_rate: Optional[float] = None
    
    @validator('total_volume_usd', 'charity_contributions', pre=True)
    def convert_to_decimal(cls, v):
        return Decimal(str(v))
    
    @property
    def duration_hours(self) -> float:
        """Calculate session duration in hours."""
        end = self.end_time or time.time()
        return (end - self.start_time) / 3600
    
    def calculate_success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_swaps == 0:
            return 0.0
        return (self.completed_swaps / self.total_swaps) * 100
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class AgentState(BaseModel):
    """Current state of the DogeSmartX agent."""
    active_swaps: Dict[str, SwapOrder] = Field(default_factory=dict)
    market_data: Dict[str, MarketData] = Field(default_factory=dict)
    gas_fees: Optional[GasFees] = None
    charity_pool: Decimal = Field(default=Decimal("0"))
    community_sentiment: str = "neutral"
    
    # Configuration state
    partial_fills_enabled: bool = True
    meme_mode: bool = True
    charity_enabled: bool = True
    
    # Session tracking
    current_session: Optional[TradingSession] = None
    
    @validator('charity_pool', pre=True)
    def convert_to_decimal(cls, v):
        return Decimal(str(v))
    
    def get_active_swap(self, swap_id: str) -> Optional[SwapOrder]:
        """Get active swap by ID."""
        return self.active_swaps.get(swap_id)
    
    def add_swap(self, swap: SwapOrder) -> None:
        """Add a new swap to active swaps."""
        self.active_swaps[swap.swap_id] = swap
    
    def update_swap(self, swap_id: str, **updates) -> bool:
        """Update an existing swap."""
        if swap_id in self.active_swaps:
            for key, value in updates.items():
                if hasattr(self.active_swaps[swap_id], key):
                    setattr(self.active_swaps[swap_id], key, value)
            self.active_swaps[swap_id].update_status()
            return True
        return False
    
    def get_fillable_swaps(self) -> List[SwapOrder]:
        """Get swaps available for partial fills."""
        return [
            swap for swap in self.active_swaps.values()
            if (swap.partial_fills_enabled and 
                swap.status in [SwapStatus.PENDING, SwapStatus.PARTIALLY_FILLED] and
                not swap.is_expired)
        ]
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }
