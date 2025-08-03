"""
DogeSmartX Agent v2.0

Main agent class for DogeSmartX operations with modular architecture.
Revolutionary AI-powered DeFi agent for cross-chain atomic swaps.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta

from pydantic import Field

from app.agent.toolcall import ToolCallAgent
from app.config import config as app_config
from app.exceptions import AgentTaskComplete
from app.logger import logger
from app.schema import Message, ToolCall
from app.tool import ToolCollection, Terminate
from app.tool.python_execute import PythonExecute
from app.tool.str_replace_editor import StrReplaceEditor
from app.tool.web_search import WebSearch

# Import modular components
from .types import AgentState, DogeSmartXConfig, OperationResult, DOGESMARTX_CAPABILITIES
from .operations import OperationRouter, ConversationalDeFiHandler
from .swap_execution import SwapExecutor, ContractDeploymentHandler
from .utilities import WalletSetupHandler, TestExecutionHandler, UtilityFunctions

# Import wallet if available
try:
    from .wallet import DogeSmartXWallet
    WALLET_AVAILABLE = True
except ImportError as e:
    logger.warning(f"DogeSmartX wallet not available: {e}")
    WALLET_AVAILABLE = False


class DogeSmartXAgent(ToolCallAgent):
    """
    DogeSmartX Agent v2.0 - Modular DeFi Agent
    
    Specialized agent for cross-chain atomic swaps, DeFi operations,
    and Sepolia testnet integration with real transaction capabilities.
    """
    
    # Agent configuration
    config: DogeSmartXConfig = Field(default_factory=DogeSmartXConfig)
    
    # Agent state
    state: AgentState = Field(default_factory=AgentState)
    
    # Operation tracking
    current_operation: str = Field(default="")
    operation_start_time: Optional[float] = Field(default=None)
    
    # DeFi-specific state
    doge_price: float = Field(default=0.0)
    eth_price: float = Field(default=0.0)
    gas_fees: Dict[str, float] = Field(default_factory=dict)
    
    # Wallet integration
    wallet_instance: Optional[Any] = Field(default=None)
    
    def __init__(self, **data):
        super().__init__(**data)
        
        # Initialize modular components
        self.operation_router = OperationRouter(self)
        self.conversational_handler = ConversationalDeFiHandler(self)
        self.swap_executor = SwapExecutor(self)
        self.contract_handler = ContractDeploymentHandler(self)
        self.wallet_handler = WalletSetupHandler(self)
        self.test_handler = TestExecutionHandler(self)
        
        # Initialize wallet if available
        if WALLET_AVAILABLE:
            self.wallet_instance = DogeSmartXWallet(testnet_mode=self.config.testnet_mode)
        
        logger.info(f"🚀 DogeSmartX Agent v{self.config.version} initialized")
        logger.info(f"🧪 Testnet mode: {self.config.testnet_mode}")
        logger.info(f"🎭 Orchestration: {'Enabled' if self.config.enable_orchestration else 'Disabled'}")

    @property
    def introduction(self) -> str:
        """Agent introduction and capabilities"""
        return f"""🚀 **DogeSmartX Agent v{self.config.version}**
═══════════════════════════════════════════════════════════════

🎯 **Specialized Capabilities:**
• 🔄 **Real Atomic Swaps**: ETH ↔ DOGE with HTLC implementation
• 🔷 **Sepolia Integration**: Real testnet deployment and monitoring
• 🐕 **Dogecoin Support**: Enhanced testnet operations
• 🔨 **Smart Contracts**: HTLC deployment on Sepolia testnet
• 🎭 **AI Orchestration**: Multi-agent coordination for complex operations
• 💰 **Wallet Management**: Dual-chain wallet with funded integration

🛠️ **Available Operations:**
• `atomic swap` - Execute cross-chain swaps
• `deploy contract` - Deploy HTLC smart contracts
• `setup wallet` - Initialize dual-chain wallets
• `test system` - Run comprehensive tests
• `conversational defi` - Natural language DeFi operations

🌟 **Revolutionary Features:**
• Real Sepolia testnet transactions
• Intelligent swap timing with market analysis
• Secure HTLC implementation with timelock protection
• Multi-agent coordination for complex requests
• Enhanced simulation with production-ready code

💡 **Ready to revolutionize your DeFi experience!**
"""

    async def step(self) -> bool:
        """Enhanced step function with modular operation routing"""
        if not self.messages:
            await self.send_introduction()
            return False

        current_message = self.messages[-1]
        if current_message.role != "user":
            return False

        # Track operation timing
        self.operation_start_time = time.time()
        
        # Route operation through modular system
        try:
            return await self.operation_router.route_operation(current_message)
        except AgentTaskComplete:
            # Calculate and log operation time
            if self.operation_start_time:
                execution_time = time.time() - self.operation_start_time
                logger.info(f"⏱️ Operation completed in {execution_time:.2f}s")
            raise
        except Exception as e:
            logger.error(f"❌ Operation failed: {e}")
            await self._send_error_response(current_message, e)
            return False

    async def send_introduction(self) -> None:
        """Send agent introduction"""
        await self.send_message(Message(role="assistant", content=self.introduction))

    # Modular operation handlers (delegated to specialized classes)
    
    async def _execute_conversational_defi(self, message: Message) -> bool:
        """Execute conversational DeFi request using orchestration engine"""
        result = await self.conversational_handler.execute_conversational_defi(message)
        
        if result.success:
            self.messages.append(Message(role="assistant", content=result.message))
            raise AgentTaskComplete(result.message)
        else:
            await self._send_error_response(message, Exception(result.message))
            return False

    async def _execute_atomic_swap(self, message: Message) -> bool:
        """Execute atomic swap operation"""
        return await self.swap_executor.execute_atomic_swap(message)

    async def _execute_contract_deployment(self, message: Message) -> bool:
        """Execute contract deployment operation"""
        return await self.contract_handler.execute_contract_deployment(message)

    async def _execute_wallet_setup(self, message: Message) -> bool:
        """Execute wallet setup operation"""
        return await self.wallet_handler.execute_wallet_setup(message)

    async def _execute_swap_test(self, message: Message) -> bool:
        """Execute test operation"""
        return await self.test_handler.execute_swap_test(message)

    async def _execute_htlc_implementation(self, message: Message) -> bool:
        """Execute HTLC implementation (alias for contract deployment)"""
        return await self._execute_contract_deployment(message)

    async def _execute_resolver_setup(self, message: Message) -> bool:
        """Execute resolver setup (placeholder for future implementation)"""
        response = """🔧 **DogeSmartX Resolver Setup**
═══════════════════════════════════════════════

⚡ **Automated Resolver Features:**
• 🤖 Intelligent swap timing
• 📊 Market condition monitoring  
• 🎯 Conditional execution logic
• 🔄 Multi-agent coordination

💡 **Currently available through orchestration engine**
Use conversational requests like:
"Swap ETH to DOGE when market conditions are optimal"

🚀 **DogeSmartX resolver integration coming soon!**
"""
        
        self.messages.append(Message(role="assistant", content=response))
        raise AgentTaskComplete(response)

    async def _fallback_operation(self, message: Message) -> bool:
        """Fallback operation for unrecognized requests"""
        try:
            # Use parent class tool calling
            return await super().step()
        except Exception as e:
            # If tool calling fails, provide helpful guidance
            fallback_response = f"""🤖 **DogeSmartX Agent**
═══════════════════════════════════════

I can help you with DeFi operations! Try these commands:

🔄 **Atomic Swaps:**
• "Execute atomic swap"
• "Swap ETH to DOGE"
• "Real cross-chain swap"

🔨 **Contract Operations:**
• "Deploy HTLC contract"
• "Deploy smart contract"

🔧 **System Operations:**
• "Setup wallet"
• "Test system"
• "Initialize DogeSmartX"

🎭 **Conversational DeFi:**
• "Swap when market is good"
• "Optimize my portfolio"
• "Help with failed transaction"

💡 **What would you like to do?**
"""
            
            self.messages.append(Message(role="assistant", content=fallback_response))
            raise AgentTaskComplete(fallback_response)

    # Utility methods

    def get_operation_expertise(self, operation_type: str) -> List[str]:
        """Get expertise information for operation type"""
        return UtilityFunctions.get_dogesmartx_expertise(operation_type)

    def get_operation_guidance(self, operation_type: str) -> List[str]:
        """Get guidance for operation type"""
        return UtilityFunctions.get_operation_guidance(operation_type)

    async def _send_error_response(self, message: Message, error: Exception) -> None:
        """Send error response to user."""
        error_message = f"""
❌ **DogeSmartX Error Response**
═══════════════════════════════════════

🚨 **Error**: {str(error)}
💡 **Suggestion**: Please check testnet connectivity and try again

🔧 **DogeSmartX can still help with:**
   • Contract deployment guidance
   • HTLC implementation advice  
   • Testnet configuration support
   • Alternative swap strategies

🎯 **Please try rephrasing your request or ask for specific assistance.**
"""
        await self.send_message(Message(role="assistant", content=error_message))

    def update_market_data(self, eth_price: float = None, doge_price: float = None):
        """Update market data for the agent"""
        if eth_price is not None:
            self.eth_price = eth_price
            self.state.eth_price = eth_price
        if doge_price is not None:
            self.doge_price = doge_price
            self.state.doge_price = doge_price
        
        logger.info(f"📊 Market data updated - ETH: ${self.eth_price}, DOGE: ${self.doge_price}")

    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "name": self.config.name,
            "version": self.config.version,
            "testnet_mode": self.config.testnet_mode,
            "current_operation": self.current_operation,
            "wallet_available": WALLET_AVAILABLE,
            "state": self.state.dict(),
            "features_enabled": self.config.features,
            "last_updated": datetime.now().isoformat()
        }


# Backward compatibility aliases
DogeSmartXSepoliaAgent = DogeSmartXAgent
DogeSmartXRevolutionaryAgent = DogeSmartXAgent  # For existing imports
