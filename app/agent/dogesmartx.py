"""
DogeSmartX Agent - Entry Point

This file provides backward compatibility while redirecting to the new modular implementation.
The modular version provides better scalability, debugging capabilities, and maintainability.
"""

# Import the new modular implementation
from .dogesmartx.agent import DogeSmartXAgent

# For backward compatibility, export the agent class
__all__ = ["DogeSmartXAgent"]

# The DogeSmartXAgent class is now imported from the modular implementation
# All functionality has been preserved and enhanced with:
# - Modular architecture for better maintainability
# - Comprehensive error handling and debugging
# - Type-safe data models with Pydantic
# - Service-based architecture for scalability
# - Enhanced configuration management
# - Professional logging and monitoring
