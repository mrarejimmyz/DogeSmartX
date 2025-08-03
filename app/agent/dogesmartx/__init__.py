"""
DogeSmartX Agent Module - Modular DeFi Cross-Chain Swap System

This module provides a scalable, debuggable architecture for DogeSmartX,
the AI-powered DeFi agent specializing in cross-chain swaps between 
Ethereum and Dogecoin.
"""

from .agent import DogeSmartXAgent
from .config import DogeSmartXConfig
from .exceptions import DogeSmartXError, SwapError, ContractError
from .models import SwapOrder, MarketData, ChainConfig

__version__ = "1.0.0"
__all__ = [
    "DogeSmartXAgent",
    "DogeSmartXConfig", 
    "DogeSmartXError",
    "SwapError",
    "ContractError",
    "SwapOrder",
    "MarketData",
    "ChainConfig"
]
