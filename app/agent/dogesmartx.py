"""
DogeSmartX Agent - Entry Point

This file provides the main entry point for the DogeSmartX agent.
Now using the Sepolia testnet specialized agent for cross-chain swaps.
"""

# Import the new Sepolia testnet implementation
from .dogesmartx.revolutionary_agent import DogeSmartXSepoliaAgent

# For backward compatibility, export the agent class
DogeSmartXAgent = DogeSmartXSepoliaAgent  # Alias for backward compatibility
__all__ = ["DogeSmartXAgent", "DogeSmartXSepoliaAgent"]

# The DogeSmartXSepoliaAgent class provides:
# - Sepolia testnet integration with 1inch Fusion+
# - HTLC atomic swap mechanisms
# - Cross-chain bridge between Sepolia ETH and Dogecoin testnet
# - Automated resolver for swap execution
# - Comprehensive testing infrastructure
# - Modular architecture for better maintainability
# - Comprehensive error handling and debugging
# - Type-safe data models with Pydantic
# - Service-based architecture for scalability
# - Enhanced configuration management
# - Professional logging and monitoring
