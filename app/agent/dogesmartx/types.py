"""
DogeSmartX Agent Types and Models
Shared data structures for the DogeSmartX agent system.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from enum import Enum
import time


class NetworkType(Enum):
    """Supported network types"""
    ETHEREUM = "ethereum"
    SEPOLIA = "sepolia"
    DOGECOIN = "dogecoin"
    DOGECOIN_TESTNET = "dogecoin_testnet"


class SwapDirection(Enum):
    """Direction of swap"""
    ETH_TO_DOGE = "eth_to_doge"
    DOGE_TO_ETH = "doge_to_eth"


class OperationType(Enum):
    """Types of DogeSmartX operations"""
    CONVERSATIONAL_DEFI = "conversational_defi"
    ATOMIC_SWAP = "atomic_swap"
    CONTRACT_DEPLOYMENT = "contract_deployment"
    WALLET_SETUP = "wallet_setup"
    RESOLVER_SETUP = "resolver_setup"
    TEST_EXECUTION = "test_execution"
    HTLC_IMPLEMENTATION = "htlc_implementation"


class SwapStatus(Enum):
    """Status of atomic swaps"""
    PENDING = "pending"
    ETH_HTLC_DEPLOYED = "eth_htlc_deployed"
    DOGE_HTLC_DEPLOYED = "doge_htlc_deployed"
    HTLCS_DEPLOYED = "htlcs_deployed"
    ETH_CLAIMED = "eth_claimed"
    DOGE_CLAIMED = "doge_claimed"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class AgentState(BaseModel):
    """State management for DogeSmartX agent operations"""
    doge_price: float = Field(default=0.0)
    eth_price: float = Field(default=0.0)
    current_operation: str = Field(default="")
    wallet_connected: bool = Field(default=False)
    testnet_mode: bool = Field(default=True)
    swap_in_progress: bool = Field(default=False)
    last_swap_id: Optional[str] = Field(default=None)
    gas_fees: Dict[str, float] = Field(default_factory=dict)
    market_conditions: Dict[str, Any] = Field(default_factory=dict)
    sepolia_connected: bool = Field(default=False)
    dogecoin_connected: bool = Field(default=False)
    orchestration_active: bool = Field(default=False)


class DogeSmartXConfig(BaseModel):
    """Configuration for DogeSmartX agent"""
    version: str = "2.0.0"
    testnet_mode: bool = True
    sepolia_rpc_url: Optional[str] = None
    dogecoin_rpc_url: Optional[str] = None
    default_timelock_hours: int = 24
    min_swap_amount_eth: float = 0.001
    max_swap_amount_eth: float = 10.0
    min_swap_amount_doge: float = 1.0
    max_swap_amount_doge: float = 100000.0
    gas_limit: int = 800000
    gas_price_multiplier: float = 1.1
    enable_orchestration: bool = True
    enable_real_swaps: bool = False
    
    # Network configurations
    sepolia_rpc_urls: List[str] = Field(default_factory=lambda: [
        "https://ethereum-sepolia.rpc.subquery.network/public",
        "https://rpc.sepolia.org",
        "https://sepolia.gateway.tenderly.co"
    ])
    
    # Feature flags
    features: Dict[str, bool] = Field(default_factory=lambda: {
        "atomic_swaps": True,
        "contract_deployment": True,
        "market_analysis": True,
        "portfolio_management": True,
        "automated_trading": True,
        "orchestration": True,
        "real_wallet_integration": True
    })


class SwapRequest(BaseModel):
    """Structured swap request data"""
    from_currency: str
    to_currency: str
    from_amount: float
    to_amount: Optional[float] = None
    recipient_address: Optional[str] = None
    timelock_hours: int = 24
    priority: str = "normal"
    conditions: Optional[Dict[str, Any]] = None


class WalletInfo(BaseModel):
    """Wallet information structure"""
    address: str
    balance_wei: Optional[int] = None
    balance_eth: Optional[float] = None
    balance_satoshi: Optional[int] = None
    balance_doge: Optional[float] = None
    chain_id: Optional[int] = None
    network: str
    connected: bool = True
    error: Optional[str] = None


class SwapExecutionResult(BaseModel):
    """Result of swap execution"""
    swap_id: str
    status: str
    eth_side: Dict[str, Any]
    doge_side: Dict[str, Any]
    swap_parameters: Dict[str, Any]
    recipients: Dict[str, str]
    next_actions: List[str]
    secret_available: bool
    is_real_swap: bool
    timestamp: str


class OperationCapability(BaseModel):
    """Capability description for operations"""
    name: str
    description: str
    requirements: List[str]
    examples: List[str]
    supported: bool = True
    testnet_only: bool = True


class OperationResult(BaseModel):
    """Result of an operation execution"""
    success: bool
    operation_type: str
    data: Dict[str, Any] = Field(default_factory=dict)
    message: str = ""
    error: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }


# Constants
SEPOLIA_CHAIN_ID = 11155111
DOGECOIN_TESTNET_MAGIC = 0x0709110b

# Default configurations
DEFAULT_SEPOLIA_RPCS = [
    "https://ethereum-sepolia.rpc.subquery.network/public",
    "https://rpc.sepolia.org",
    "https://sepolia.gateway.tenderly.co"
]

DEFAULT_DOGECOIN_RPCS = [
    "http://localhost:22555",
    "https://api.dogecoin.org/testnet"
]

# Operation capabilities
DOGESMARTX_CAPABILITIES = {
    "atomic_swaps": OperationCapability(
        name="Cross-Chain Atomic Swaps",
        description="Execute real atomic swaps between ETH and DOGE using HTLCs",
        requirements=["Sepolia testnet connection", "Dogecoin testnet wallet"],
        examples=[
            "Swap 0.001 ETH to 10 DOGE",
            "Execute atomic swap with 24 hour timelock",
            "Deploy HTLC contracts on both chains"
        ]
    ),
    "conversational_defi": OperationCapability(
        name="Conversational DeFi Interface",
        description="Natural language interface for DeFi operations with AI orchestration",
        requirements=["Orchestration engine", "LLM integration"],
        examples=[
            "I want to swap ETH to DOGE when market conditions are optimal",
            "Manage my portfolio automatically",
            "Monitor and execute trades based on sentiment"
        ]
    ),
    "contract_deployment": OperationCapability(
        name="Smart Contract Deployment",
        description="Deploy HTLC and other contracts on Sepolia testnet",
        requirements=["Sepolia testnet connection", "Funded wallet"],
        examples=[
            "Deploy HTLC contract for atomic swaps",
            "Deploy limit order contracts",
            "Deploy charity pool contracts"
        ]
    ),
    "wallet_management": OperationCapability(
        name="Multi-Chain Wallet Management",
        description="Manage ETH and DOGE wallets for cross-chain operations",
        requirements=["Web3 libraries", "Secure key storage"],
        examples=[
            "Initialize Sepolia testnet wallet",
            "Create Dogecoin testnet wallet",
            "Check wallet balances and status"
        ]
    )
}


class ChainConfig(BaseModel):
    """Configuration for a blockchain network"""
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
    """Market data for trading pairs"""
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


class SwapOrder(BaseModel):
    """A cross-chain swap order"""
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
    
    @validator('amount', 'filled_amount', 'exchange_rate', 'slippage_tolerance', 'charity_contribution', pre=True)
    def convert_to_decimal(cls, v):
        if v is None:
            return v
        return Decimal(str(v))
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }
