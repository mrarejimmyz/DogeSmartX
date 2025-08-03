"""
DogeSmartX Agent Module v2.0 - Modular Cross-Chain DeFi System

This module provides the DogeSmartX agent system for cross-chain atomic swaps,
smart contract deployment, and DeFi operations with Sepolia testnet integration.
"""

# Import new modular components
from .agent import DogeSmartXAgent, DogeSmartXSepoliaAgent, DogeSmartXRevolutionaryAgent
from .types import AgentState, DogeSmartXConfig, OperationResult, SwapRequest
from .operations import OperationDetector, OperationRouter, ConversationalDeFiHandler
from .swap_execution import SwapExecutor, ContractDeploymentHandler
from .utilities import WalletSetupHandler, TestExecutionHandler, UtilityFunctions

# Import existing components for backward compatibility
try:
    from .wallet import DogeSmartXWallet
    WALLET_AVAILABLE = True
except ImportError:
    WALLET_AVAILABLE = False

try:
    from .orchestration_engine import get_dogesmartx_orchestrator, process_conversational_request
    ORCHESTRATION_AVAILABLE = True
except ImportError:
    ORCHESTRATION_AVAILABLE = False

try:
    from .sepolia_config import sepolia_config, SepoliaDogeSmartXConfig
    from .exceptions import DogeSmartXError, SwapError, ContractError
    from .types import SwapOrder, MarketData, ChainConfig
    LEGACY_COMPONENTS_AVAILABLE = True
except ImportError:
    LEGACY_COMPONENTS_AVAILABLE = False

# Main exports
__version__ = "2.0.0"
__all__ = [
    # Main agent class
    "DogeSmartXAgent",
    
    # Modular components
    "AgentState",
    "DogeSmartXConfig", 
    "OperationResult",
    "SwapRequest",
    "OperationDetector",
    "OperationRouter",
    "ConversationalDeFiHandler",
    "SwapExecutor",
    "ContractDeploymentHandler",
    "WalletSetupHandler",
    "TestExecutionHandler",
    "UtilityFunctions",
    
    # Backward compatibility
    "DogeSmartXSepoliaAgent",
    "DogeSmartXRevolutionaryAgent", 
]

# Conditional exports for optional components
if WALLET_AVAILABLE:
    __all__.extend(["DogeSmartXWallet"])

if ORCHESTRATION_AVAILABLE:
    __all__.extend(["get_dogesmartx_orchestrator", "process_conversational_request"])

if LEGACY_COMPONENTS_AVAILABLE:
    __all__.extend([
        "sepolia_config",
        "SepoliaDogeSmartXConfig", 
        "DogeSmartXError",
        "SwapError",
        "ContractError",
        "SwapOrder",
        "MarketData", 
        "ChainConfig"
    ])

# Feature availability info
def get_available_features():
    """Get information about available DogeSmartX features"""
    return {
        "wallet_integration": WALLET_AVAILABLE,
        "orchestration_engine": ORCHESTRATION_AVAILABLE,
        "legacy_components": LEGACY_COMPONENTS_AVAILABLE,
        "version": __version__
    }
