"""
DogeSmartX Sepolia Testnet Configuration

Specialized configuration for testing 1inch Fusion+ cross-chain swaps
between Sepolia ETH and Dogecoin testnet using HTLC mechanisms.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from decimal import Decimal
from pydantic import BaseModel


@dataclass
class SepoliaNetworkConfig:
    """Sepolia testnet configuration for ETH operations."""
    name: str = "sepolia"
    rpc_url: str = "https://sepolia.infura.io/v3/YOUR_INFURA_KEY"
    chain_id: int = 11155111
    min_confirmations: int = 1  # Faster for testing
    gas_limit: int = 500000  # Higher for complex operations
    gas_price_gwei: float = 20.0  # Conservative for testnet
    block_time: int = 12  # Seconds per block
    
    # Sepolia faucets for test ETH
    faucets: List[str] = field(default_factory=lambda: [
        "https://sepoliafaucet.com/",
        "https://faucet.sepolia.dev/",
        "https://faucet.quicknode.com/ethereum/sepolia"
    ])
    
    # Sepolia block explorer
    explorer_url: str = "https://sepolia.etherscan.io"


@dataclass  
class DogecoinTestnetConfig:
    """Dogecoin testnet configuration for DOGE operations."""
    name: str = "dogecoin_testnet"
    rpc_url: str = "https://dogecoin-testnet.public-rpc.com"
    network_magic: str = "testnet3"
    min_confirmations: int = 2  # Faster for testing
    block_time: int = 60  # Seconds per block
    
    # Dogecoin testnet faucets
    faucets: List[str] = field(default_factory=lambda: [
        "https://testnet-faucet.multidoge.org/",
        "https://faucet.dogecoin-info.net/",
        "https://faucetpay.io/faucet/dogecoin"
    ])
    
    # Dogecoin testnet explorer
    explorer_url: str = "https://sochain.com/testnet/doge"


@dataclass
class HTLCConfig:
    """Hash Time-Locked Contract configuration."""
    # Time settings
    default_timelock_hours: int = 24  # 24 hours for swap completion
    safety_margin_hours: int = 2  # Safety margin before timelock
    min_timelock_hours: int = 1  # Minimum timelock duration
    max_timelock_hours: int = 72  # Maximum timelock duration
    
    # Hash settings
    hash_algorithm: str = "sha256"
    secret_length: int = 32  # 32 bytes for secret
    
    # Contract addresses (will be set after deployment)
    sepolia_htlc_contract: str = ""  # To be deployed
    fusion_plus_contract: str = ""  # To be deployed


@dataclass
class FusionPlusConfig:
    """1inch Fusion+ configuration for Sepolia testnet."""
    # Contract addresses (to be deployed)
    limit_order_protocol: str = ""
    fusion_resolver: str = ""
    settlement_contract: str = ""
    
    # Testing parameters
    min_swap_amount_eth: Decimal = Decimal("0.001")  # 0.001 ETH minimum
    max_swap_amount_eth: Decimal = Decimal("1.0")    # 1 ETH maximum for testing
    min_swap_amount_doge: Decimal = Decimal("100")   # 100 DOGE minimum
    max_swap_amount_doge: Decimal = Decimal("10000") # 10,000 DOGE maximum
    
    # Fee structure for testing
    resolver_fee_bps: int = 30  # 0.3% resolver fee
    protocol_fee_bps: int = 10  # 0.1% protocol fee
    
    # Slippage and price tolerance
    max_slippage_bps: int = 100  # 1% max slippage
    price_tolerance_bps: int = 50  # 0.5% price tolerance


@dataclass
class ResolverConfig:
    """Resolver service configuration for automated swaps."""
    # Monitoring settings
    poll_interval_seconds: int = 10  # Check for new swaps every 10 seconds
    max_pending_swaps: int = 10  # Maximum concurrent swaps
    
    # Security settings
    require_confirmations_eth: int = 1  # ETH confirmations required
    require_confirmations_doge: int = 2  # DOGE confirmations required
    
    # Wallet settings
    eth_private_key: str = ""  # Will be loaded from environment
    doge_private_key: str = ""  # Will be loaded from environment
    
    # Operational limits
    max_eth_exposure: Decimal = Decimal("5.0")  # Max 5 ETH at risk
    max_doge_exposure: Decimal = Decimal("50000")  # Max 50k DOGE at risk


@dataclass
class TestingConfig:
    """Testing and development configuration."""
    # Test accounts
    test_eth_addresses: List[str] = field(default_factory=list)
    test_doge_addresses: List[str] = field(default_factory=list)
    
    # Simulation settings
    simulate_resolver: bool = True  # Use simulated resolver for testing
    auto_fund_accounts: bool = True  # Auto-request faucet funds
    log_all_transactions: bool = True  # Detailed logging
    
    # Development features
    enable_debug_mode: bool = True
    mock_price_feeds: bool = False  # Use real price feeds by default
    fast_timelock_testing: bool = True  # Shorter timelocks for testing


@dataclass
class SepoliaDogeSmartXConfig:
    """Complete Sepolia testnet configuration for DogeSmartX."""
    
    # Agent settings
    name: str = "DogeSmartX-Sepolia-Testnet"
    version: str = "2.0-sepolia"
    environment: str = "sepolia_testnet"
    
    # Network configurations
    sepolia: SepoliaNetworkConfig = field(default_factory=SepoliaNetworkConfig)
    dogecoin_testnet: DogecoinTestnetConfig = field(default_factory=DogecoinTestnetConfig)
    
    # Protocol configurations
    htlc: HTLCConfig = field(default_factory=HTLCConfig)
    fusion_plus: FusionPlusConfig = field(default_factory=FusionPlusConfig)
    resolver: ResolverConfig = field(default_factory=ResolverConfig)
    testing: TestingConfig = field(default_factory=TestingConfig)
    
    # Security settings
    max_gas_price_gwei: float = 100.0  # Max gas price protection
    slippage_protection: float = 0.05  # 5% max slippage
    
    # Performance settings
    cache_price_data_seconds: int = 30  # Cache price data for 30 seconds
    transaction_timeout_seconds: int = 300  # 5 minute transaction timeout
    
    # Feature flags
    enable_cross_chain_swaps: bool = True
    enable_atomic_swaps: bool = True
    enable_automated_resolver: bool = True
    enable_community_features: bool = True
    
    def __post_init__(self):
        """Post-initialization validation and setup."""
        self._load_environment_variables()
        self._validate_configuration()
    
    def _load_environment_variables(self):
        """Load sensitive configuration from environment variables."""
        # Load RPC URLs
        if infura_key := os.getenv("INFURA_API_KEY"):
            self.sepolia.rpc_url = f"https://sepolia.infura.io/v3/{infura_key}"
        
        if alchemy_key := os.getenv("ALCHEMY_API_KEY"):
            self.sepolia.rpc_url = f"https://eth-sepolia.g.alchemy.com/v2/{alchemy_key}"
        
        # Load private keys (for resolver)
        if eth_key := os.getenv("SEPOLIA_PRIVATE_KEY"):
            self.resolver.eth_private_key = eth_key
            
        if doge_key := os.getenv("DOGECOIN_TESTNET_PRIVATE_KEY"):
            self.resolver.doge_private_key = doge_key
        
        # Load contract addresses if deployed
        if htlc_contract := os.getenv("SEPOLIA_HTLC_CONTRACT"):
            self.htlc.sepolia_htlc_contract = htlc_contract
            
        if fusion_contract := os.getenv("SEPOLIA_FUSION_CONTRACT"):
            self.fusion_plus.limit_order_protocol = fusion_contract
    
    def _validate_configuration(self):
        """Validate the configuration for common issues."""
        # Only validate if not in development/testing mode
        if not self.testing.enable_debug_mode:
            # Validate network settings
            if not self.sepolia.rpc_url or "YOUR_" in self.sepolia.rpc_url:
                raise ValueError("Valid Sepolia RPC URL required. Set INFURA_API_KEY or ALCHEMY_API_KEY environment variable.")
        
        # Validate timelock settings
        if self.htlc.min_timelock_hours >= self.htlc.default_timelock_hours:
            raise ValueError("Minimum timelock must be less than default timelock")
        
        # Validate swap limits
        if self.fusion_plus.min_swap_amount_eth >= self.fusion_plus.max_swap_amount_eth:
            raise ValueError("Minimum ETH swap amount must be less than maximum")
    
    def get_network_config(self, network: str) -> Dict[str, Any]:
        """Get network configuration by name."""
        if network.lower() == "sepolia":
            return {
                "name": self.sepolia.name,
                "rpc_url": self.sepolia.rpc_url,
                "chain_id": self.sepolia.chain_id,
                "explorer_url": self.sepolia.explorer_url
            }
        elif network.lower() in ["dogecoin", "doge", "dogecoin_testnet"]:
            return {
                "name": self.dogecoin_testnet.name,
                "rpc_url": self.dogecoin_testnet.rpc_url,
                "network_magic": self.dogecoin_testnet.network_magic,
                "explorer_url": self.dogecoin_testnet.explorer_url
            }
        else:
            raise ValueError(f"Unknown network: {network}")
    
    def is_testnet_ready(self) -> bool:
        """Check if configuration is ready for testnet operations."""
        checks = [
            bool(self.sepolia.rpc_url and "YOUR_" not in self.sepolia.rpc_url),
            bool(self.dogecoin_testnet.rpc_url),
            self.sepolia.chain_id == 11155111,  # Sepolia chain ID
            self.environment == "sepolia_testnet"
        ]
        return all(checks)
    
    def get_faucet_urls(self) -> Dict[str, List[str]]:
        """Get faucet URLs for both networks."""
        return {
            "sepolia_eth": self.sepolia.faucets,
            "dogecoin_testnet": self.dogecoin_testnet.faucets
        }
    
    def get_explorer_urls(self) -> Dict[str, str]:
        """Get block explorer URLs for both networks."""
        return {
            "sepolia": self.sepolia.explorer_url,
            "dogecoin_testnet": self.dogecoin_testnet.explorer_url
        }


# Create the global configuration instance
sepolia_config = SepoliaDogeSmartXConfig()

# Backwards compatibility
config = sepolia_config
