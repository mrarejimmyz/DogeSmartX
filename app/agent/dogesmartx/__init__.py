"""
DogeSmartX Agent Module - Sepolia Testnet Cross-Chain Swap System

This module provides the DogeSmartX Sepolia testnet agent for testing
1inch Fusion+ cross-chain swaps between Sepolia ETH and Dogecoin testnet
using HTLC (Hash Time-Locked Contract) mechanisms.
"""

from .revolutionary_agent import DogeSmartXSepoliaAgent, DogeSmartXRevolutionaryAgent
from .sepolia_config import sepolia_config, SepoliaDogeSmartXConfig
from .exceptions import DogeSmartXError, SwapError, ContractError
from .models import SwapOrder, MarketData, ChainConfig

# Backward compatibility
DogeSmartXAgent = DogeSmartXSepoliaAgent
DogeSmartXConfig = SepoliaDogeSmartXConfig

__version__ = "2.0.0-sepolia"
__all__ = [
    "DogeSmartXSepoliaAgent",
    "DogeSmartXRevolutionaryAgent", 
    "DogeSmartXAgent",  # Backward compatibility
    "SepoliaDogeSmartXConfig",
    "DogeSmartXConfig",  # Backward compatibility
    "DogeSmartXError",
    "SwapError",
    "ContractError",
    "SwapOrder",
    "MarketData",
    "ChainConfig"
]
