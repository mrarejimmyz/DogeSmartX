"""
DogeSmartX Configuration Module

Centralized configuration management for DogeSmartX agent with environment-specific
settings, network configurations, and feature flags.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pydantic import BaseModel


@dataclass
class NetworkConfig:
    """Network configuration for blockchain connections."""
    name: str
    rpc_url: str
    chain_id: Optional[int] = None
    min_confirmations: int = 3
    gas_limit: int = 300000
    gas_price_gwei: float = 50.0
    
    def __post_init__(self):
        if not self.rpc_url:
            raise ValueError(f"RPC URL required for {self.name}")


@dataclass
class ContractConfig:
    """Smart contract configuration."""
    address: str
    abi_path: Optional[str] = None
    deployment_block: Optional[int] = None
    
    @property
    def is_deployed(self) -> bool:
        """Check if contract is deployed (has valid address)."""
        return self.address and self.address != "0x" and len(self.address) == 42


@dataclass
class DogeSmartXConfig:
    """Main configuration class for DogeSmartX agent."""
    
    # Agent settings
    name: str = "DogeSmartX"
    version: str = "1.0.0"
    max_steps: int = 25
    max_observe: int = 20000
    debug_mode: bool = False
    
    # Feature flags
    partial_fills_enabled: bool = True
    charity_enabled: bool = True
    meme_mode: bool = True
    community_features: bool = True
    
    # Trading settings
    charity_fee_percentage: float = 0.1
    min_swap_amount: float = 0.001
    max_swap_amount: float = 1000.0
    default_timelock_hours: int = 24
    
    # Network configurations
    networks: Dict[str, NetworkConfig] = field(default_factory=lambda: {
        "ethereum": NetworkConfig(
            name="sepolia",
            rpc_url=os.getenv("ETH_RPC_URL", "https://sepolia.infura.io/v3/"),
            chain_id=11155111,
            min_confirmations=3,
            gas_limit=300000
        ),
        "dogecoin": NetworkConfig(
            name="testnet",
            rpc_url=os.getenv("DOGE_RPC_URL", "http://localhost:18332"),
            min_confirmations=6
        )
    })
    
    # Contract configurations
    contracts: Dict[str, ContractConfig] = field(default_factory=lambda: {
        "limit_order_protocol": ContractConfig(
            address=os.getenv("LIMIT_ORDER_PROTOCOL_ADDRESS", "0x"),
            abi_path="contracts/abi/LimitOrderProtocol.json"
        ),
        "doge_bridge": ContractConfig(
            address=os.getenv("DOGE_BRIDGE_ADDRESS", "0x"),
            abi_path="contracts/abi/DogeBridge.json"
        ),
        "charity_pool": ContractConfig(
            address=os.getenv("CHARITY_POOL_ADDRESS", "0x"),
            abi_path="contracts/abi/CharityPool.json"
        )
    })
    
    # API configurations
    api_keys: Dict[str, str] = field(default_factory=lambda: {
        "infura": os.getenv("INFURA_API_KEY", ""),
        "coingecko": os.getenv("COINGECKO_API_KEY", ""),
        "1inch": os.getenv("ONEINCH_API_KEY", ""),
        "twitter": os.getenv("TWITTER_API_KEY", "")
    })
    
    # Logging configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "DogeSmartXConfig":
        """Create configuration from environment variables."""
        return cls(
            debug_mode=os.getenv("DOGESMARTX_DEBUG", "false").lower() == "true",
            partial_fills_enabled=os.getenv("PARTIAL_FILLS", "true").lower() == "true",
            charity_enabled=os.getenv("CHARITY_ENABLED", "true").lower() == "true",
            meme_mode=os.getenv("MEME_MODE", "true").lower() == "true",
            charity_fee_percentage=float(os.getenv("CHARITY_FEE", "0.1")),
            min_swap_amount=float(os.getenv("MIN_SWAP", "0.001")),
            max_swap_amount=float(os.getenv("MAX_SWAP", "1000.0")),
            default_timelock_hours=int(os.getenv("TIMELOCK_HOURS", "24"))
        )
    
    def get_network(self, name: str) -> NetworkConfig:
        """Get network configuration by name."""
        if name not in self.networks:
            raise ValueError(f"Network '{name}' not configured")
        return self.networks[name]
    
    def get_contract(self, name: str) -> ContractConfig:
        """Get contract configuration by name."""
        if name not in self.contracts:
            raise ValueError(f"Contract '{name}' not configured")
        return self.contracts[name]
    
    def is_contract_deployed(self, name: str) -> bool:
        """Check if a contract is deployed."""
        try:
            return self.get_contract(name).is_deployed
        except ValueError:
            return False
    
    def validate(self) -> None:
        """Validate configuration settings."""
        errors = []
        
        # Validate fee percentage
        if not 0 <= self.charity_fee_percentage <= 100:
            errors.append("Charity fee percentage must be between 0-100")
        
        # Validate swap amounts
        if self.min_swap_amount <= 0:
            errors.append("Minimum swap amount must be positive")
        
        if self.max_swap_amount <= self.min_swap_amount:
            errors.append("Maximum swap amount must be greater than minimum")
        
        # Validate timelock
        if self.default_timelock_hours <= 0:
            errors.append("Timelock hours must be positive")
        
        # Validate networks
        for name, network in self.networks.items():
            if not network.rpc_url:
                errors.append(f"RPC URL required for network '{name}'")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")


# Global configuration instance
config = DogeSmartXConfig.from_env()
