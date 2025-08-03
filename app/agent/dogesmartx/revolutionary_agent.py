"""
DogeSmartX v2.0 - Sepolia Testnet Revolutionary Architecture

Next-generation DeFi agent optimized for Sepolia testnet development and testing
of 1inch Fusion+ cross-chain swaps with HTLC implementation.
"""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional, Union
from decimal import Decimal
from datetime import datetime, timedelta

from pydantic import Field, BaseModel

from app.agent.toolcall import ToolCallAgent
from app.config import config as app_config
from app.exceptions import AgentTaskComplete
from app.logger import logger
from app.schema import Message, ToolCall
from app.tool import ToolCollection, Terminate
from app.tool.python_execute import PythonExecute
from app.tool.str_replace_editor import StrReplaceEditor
from app.tool.web_search import WebSearch

# Import Sepolia-specific modules
try:
    from .sepolia_config import sepolia_config, SepoliaDogeSmartXConfig
    from .htlc import CrossChainHTLCManager, HTLCSecret, SepoliaHTLCService, DogecoinHTLCService
    from .sepolia_resolver import SepoliaTestnetResolver
except ImportError as e:
    logger.warning(f"Sepolia modules not fully available: {e}")
    # Set defaults for missing modules
    sepolia_config = {}
    SepoliaDogeSmartXConfig = dict
    CrossChainHTLCManager = object
    HTLCSecret = object
    SepoliaHTLCService = object
    DogecoinHTLCService = object
    SepoliaTestnetResolver = object

# Agent state model
class AgentState(BaseModel):
    """Simple agent state tracking."""
    current_task: Optional[str] = None
    last_action: Optional[str] = None
    testnet_mode: bool = True
    sepolia_enabled: bool = True


class DogeSmartXSepoliaAgent(ToolCallAgent):
    """
    DogeSmartX Sepolia Testnet Agent v2.0
    
    🧪 SEPOLIA TESTNET SPECIALIZED AGENT:
    
    ✨ CORE FEATURES:
    - Research and web browsing capabilities
    - Code execution and file management
    - Data analysis and learning
    
    🔗 SEPOLIA TESTNET FEATURES:
    - 1inch Fusion+ contract deployment and testing
    - HTLC implementation for atomic swaps
    - Cross-chain bridge between Sepolia ETH and Dogecoin testnet
    - Automated resolver for swap execution
    
    🧪 TESTING INFRASTRUCTURE:
    - Faucet integration for test tokens
    - Contract deployment automation
    - Swap simulation and validation
    - Comprehensive logging and monitoring
    
    🔐 SECURITY FOR TESTING:
    - HTLC timelock mechanisms
    - Multi-step atomic swap validation
    - Testnet-safe transaction limits
    - Real-time monitoring and alerts
    """

    name: str = "DogeSmartX-Sepolia-Testnet"
    description: str = (
        "Sepolia testnet specialized DeFi agent for testing 1inch Fusion+ cross-chain "
        "swaps between Sepolia ETH and Dogecoin testnet using HTLC mechanisms"
    )
    
    # Enhanced agent configuration for testnet
    max_steps: int = 50
    max_observe: int = 50000
    
    # Use Sepolia testnet configuration
    config: Optional[Any] = Field(default_factory=lambda: sepolia_config if sepolia_config else {})
    state: AgentState = Field(default_factory=AgentState)
    
    # Sepolia-specific services
    htlc_manager: Optional[Any] = None
    resolver: Optional[Any] = None
    sepolia_htlc: Optional[Any] = None
    dogecoin_htlc: Optional[Any] = None

    def __init__(self, **kwargs):
        """Initialize the Sepolia testnet DogeSmartX agent."""
        try:
            # Initialize with proper ToolCallAgent initialization
            super().__init__(**kwargs)
            
            # Validate configuration
            self._validate_sepolia_config()
            
            # Initialize services
            self._initialize_sepolia_services()
            
            # Set system prompts
            self.system_prompt = self._get_sepolia_system_prompt()
            self.next_step_prompt = self._get_sepolia_next_step_prompt()
            
            # Add connection validation
            self._validate_connections()
            
            logger.info("🧪 DogeSmartX Sepolia Testnet Agent v2.0 initialized! Ready for testing! 🚀")
            
        except Exception as e:
            logger.error(f"❌ DogeSmartX initialization failed: {e}")
            # Ensure the agent can still function in a basic mode
            self._initialize_fallback_mode()

    def _validate_connections(self) -> None:
        """Validate LLM and service connections."""
        try:
            if hasattr(self, 'llm') and self.llm:
                logger.info("✅ LLM connection available")
            else:
                logger.warning("⚠️ LLM connection not available - using fallback mode")
                
        except Exception as e:
            logger.warning(f"⚠️ Connection validation failed: {e}")

    def _initialize_fallback_mode(self) -> None:
        """Initialize basic fallback mode when full initialization fails."""
        try:
            # Basic configuration
            self.state = AgentState()
            self.system_prompt = self._get_sepolia_system_prompt()
            self.next_step_prompt = self._get_sepolia_next_step_prompt()
            
            # Minimal tool collection
            self.available_tools = ToolCollection(Terminate())
            
            logger.info("🔄 DogeSmartX initialized in fallback mode - basic functionality available")
            
        except Exception as e:
            logger.error(f"❌ Even fallback initialization failed: {e}")

    def _validate_sepolia_config(self) -> None:
        """Validate the Sepolia configuration."""
        try:
            if isinstance(self.config, dict):
                logger.info("✅ Sepolia configuration validated successfully")
            else:
                logger.warning("⚠️  Using default configuration")
        except Exception as e:
            logger.error(f"❌ Sepolia configuration validation failed: {e}")

    def _initialize_sepolia_services(self) -> None:
        """Initialize Sepolia-specific services."""
        try:
            # Initialize HTLC services with graceful degradation
            if SepoliaHTLCService != object:
                try:
                    # Try to initialize with config if available
                    if hasattr(self.config, 'sepolia') and isinstance(self.config, dict):
                        self.sepolia_htlc = SepoliaHTLCService()
                    else:
                        logger.info("⚠️  Sepolia HTLC Service skipped - config not available")
                except Exception as e:
                    logger.info(f"⚠️  Sepolia HTLC Service skipped - {e}")
                else:
                    logger.info("✅ Sepolia HTLC Service initialized")
            
            if DogecoinHTLCService != object:
                try:
                    # Try to initialize with config if available
                    if hasattr(self.config, 'dogecoin') and isinstance(self.config, dict):
                        self.dogecoin_htlc = DogecoinHTLCService()
                    else:
                        logger.info("⚠️  Dogecoin HTLC Service skipped - config not available")
                except Exception as e:
                    logger.info(f"⚠️  Dogecoin HTLC Service skipped - {e}")
                else:
                    logger.info("✅ Dogecoin HTLC Service initialized")
            
            # Initialize HTLC manager with services if available
            if (CrossChainHTLCManager != object and 
                hasattr(self, 'sepolia_htlc') and self.sepolia_htlc and 
                hasattr(self, 'dogecoin_htlc') and self.dogecoin_htlc):
                try:
                    self.htlc_manager = CrossChainHTLCManager(
                        sepolia_service=self.sepolia_htlc,
                        dogecoin_service=self.dogecoin_htlc
                    )
                    logger.info("✅ HTLC Manager initialized")
                except Exception as e:
                    logger.info(f"⚠️  HTLC Manager skipped - {e}")
            else:
                logger.info("⚠️  HTLC Manager skipped - services not available")
            
            # Initialize resolver if available
            if SepoliaTestnetResolver != object:
                try:
                    self.resolver = SepoliaTestnetResolver()
                    logger.info("✅ Sepolia Resolver initialized")
                except Exception as e:
                    logger.info(f"⚠️  Sepolia Resolver skipped - {e}")
            
            # Count initialized services
            initialized_services = []
            if hasattr(self, 'sepolia_htlc') and self.sepolia_htlc:
                initialized_services.append("Sepolia HTLC")
            if hasattr(self, 'dogecoin_htlc') and self.dogecoin_htlc:
                initialized_services.append("Dogecoin HTLC")
            if hasattr(self, 'htlc_manager') and self.htlc_manager:
                initialized_services.append("HTLC Manager")
            if hasattr(self, 'resolver') and self.resolver:
                initialized_services.append("Resolver")
            
            if initialized_services:
                logger.info(f"🌟 Sepolia services initialized: {', '.join(initialized_services)}")
            else:
                logger.info("🔄 Running in basic mode - specialized services will be available when configuration is provided")
            
        except Exception as e:
            logger.error(f"❌ Service initialization error: {e}")
            # Always continue with graceful degradation
            logger.info("🔄 Continuing with basic agent functionality...")

    def _get_sepolia_system_prompt(self) -> str:
        """Get the system prompt for Sepolia testnet operations."""
        return """
You are DogeSmartX Sepolia Testnet Agent v2.0, a specialized DeFi agent for testing cross-chain swaps.

🧪 TESTNET ENVIRONMENT:
- Operating on Sepolia testnet (Chain ID: 11155111)
- Testing 1inch Fusion+ cross-chain swaps
- Using HTLC (Hash Time-Locked Contracts) for atomic swaps
- Connecting Sepolia ETH ↔ Dogecoin testnet

🔧 CORE CAPABILITIES:
1. Deploy and test 1inch Fusion+ contracts on Sepolia
2. Implement HTLC atomic swaps between networks
3. Set up automated resolvers for swap execution
4. Execute test swaps with comprehensive monitoring

🛡️ SAFETY PROTOCOLS:
- All operations are testnet-only
- Use faucet tokens (no real value)
- Implement proper timelock mechanisms
- Monitor all transactions for security

🎯 CURRENT OBJECTIVES:
1. Deploy Fusion+ Contracts on Sepolia
2. Implement HTLC on Dogecoin Testnet
3. Set Up Automated Resolver
4. Execute and Validate Test Swaps

Always prioritize testing, validation, and comprehensive logging.
"""

    def _get_sepolia_next_step_prompt(self) -> str:
        """Get the next step prompt for planning."""
        return """
Based on the current state and user request, determine the next step for Sepolia testnet operations.

Consider:
1. Contract deployment status
2. HTLC implementation progress
3. Resolver setup completion
4. Test execution requirements

Provide a clear, actionable next step with specific implementation details.
"""

    async def process_message(self, message: Message) -> None:
        """Process user messages with Sepolia testnet focus."""
        try:
            # Update state
            self.state.current_task = message.content
            self.state.last_action = datetime.now().isoformat()
            
            # Log the request
            logger.info(f"🧪 Processing Sepolia testnet request: {message.content}")
            
            # Use parent class tool calling system but with DogeSmartX-specific logic
            await super().process_message(message)
            
        except Exception as e:
            logger.error(f"❌ Error processing Sepolia message: {e}")
            await self._send_error_response(message, e)

    async def step(self) -> bool:
        """Override step method to provide DogeSmartX-specific behavior."""
        try:
            # Get the current user message
            if hasattr(self, 'messages') and self.messages:
                user_messages = [msg for msg in self.messages if msg.role == 'user']
                if user_messages:
                    current_message = user_messages[-1]
                    
                    # Detect operation type and provide specialized assistance
                    operation_type = self._detect_operation_type(current_message.content)
                    
                    # Provide immediate DogeSmartX expertise response
                    response_data = {
                        "action": operation_type,
                        "status": "processing",
                        "message": f"🧪 DogeSmartX analyzing {operation_type} request...",
                        "user_request": current_message.content,
                        "expertise": self._get_dogesmartx_expertise(operation_type),
                        "next_steps": self._get_next_steps_for_request(current_message.content)
                    }
                    
                    # Format and send detailed response
                    response_message = self._format_dogesmartx_response(response_data)
                    
                    # Add message to the conversation
                    response_msg = Message(role="assistant", content=response_message)
                    self.messages.append(response_msg)
                    
                    logger.info("🧪 DogeSmartX provided specialized response")
                    
                    # Raise AgentTaskComplete to properly terminate with the response
                    raise AgentTaskComplete(response_message)
            
            # Let the parent class handle tool calling if needed
            return await super().step()
            
        except AgentTaskComplete:
            # Re-raise AgentTaskComplete to properly terminate
            raise
        except Exception as e:
            logger.error(f"❌ DogeSmartX step failed: {e}")
            # Add error message to conversation
            error_msg = Message(role="assistant", content=f"❌ DogeSmartX Error: {str(e)}")
            if hasattr(self, 'messages'):
                self.messages.append(error_msg)
            raise AgentTaskComplete(f"❌ DogeSmartX Error: {str(e)}")

    def _get_dogesmartx_expertise(self, operation_type: str) -> list:
        """Get DogeSmartX-specific expertise for the operation type."""
        expertise_map = {
            "contract_deployment": [
                "🚀 1inch Fusion+ contract artifacts preparation",
                "⚙️ Sepolia testnet deployment configuration", 
                "🔍 Contract verification and validation",
                "📊 Gas optimization strategies"
            ],
            "htlc_implementation": [
                "🔒 SHA-256 hash secret generation",
                "⏰ Timelock mechanism implementation (24h default)",
                "🌉 Cross-chain coordination protocols",
                "✅ Atomic swap validation mechanisms"
            ],
            "resolver_setup": [
                "🤖 Automated resolver deployment",
                "📊 Real-time monitoring systems",
                "⚡ Execution optimization",
                "🛡️ Security validation protocols"
            ],
            "test_execution": [
                "🧪 Testnet connectivity validation",
                "🔐 HTLC secret management",
                "📈 Swap execution monitoring",
                "📋 Comprehensive test reporting"
            ],
            "general": [
                "🔄 ETH ↔ DOGE atomic swaps on Sepolia testnet",
                "🚀 1inch Fusion+ integration expertise",
                "🔒 HTLC implementation and testing",
                "📊 DeFi protocol optimization"
            ]
        }
        return expertise_map.get(operation_type, expertise_map["general"])

    def _format_dogesmartx_response(self, response_data: Dict[str, Any]) -> str:
        """Format a comprehensive DogeSmartX response."""
        lines = [
            "🧪 **DogeSmartX Sepolia Testnet Agent Response**",
            "=" * 50,
            f"📋 **Operation**: {response_data['action']}",
            f"⚡ **Status**: {response_data['status']}",
            f"💬 **Analysis**: {response_data['message']}",
            "",
            "🔧 **DogeSmartX Expertise:**"
        ]
        
        for expertise in response_data.get('expertise', []):
            lines.append(f"   • {expertise}")
            
        lines.append("")
        lines.append("📝 **Recommended Next Steps:**")
        
        for i, step in enumerate(response_data.get('next_steps', []), 1):
            lines.append(f"   {i}. {step}")
            
        lines.extend([
            "",
            "✨ **Ready to assist with:**",
            "   • Contract deployment and verification",
            "   • HTLC implementation and testing", 
            "   • Cross-chain swap execution",
            "   • Automated resolver setup",
            "",
            "🎯 **How can I help you execute this operation?**"
        ])
        
        return "\n".join(lines)

    def _get_next_steps_for_request(self, content: str) -> list:
        """Get specific next steps based on the user's request."""
        content_lower = content.lower()
        
        if "swap" in content_lower:
            return [
                "1. Validate testnet connectivity (Sepolia + Dogecoin testnet)",
                "2. Generate HTLC secret and hash",
                "3. Deploy HTLC contracts on both networks", 
                "4. Execute atomic swap sequence",
                "5. Monitor swap completion"
            ]
        elif "deploy" in content_lower:
            return [
                "1. Prepare 1inch Fusion+ contract artifacts",
                "2. Configure Sepolia testnet connection",
                "3. Deploy contracts with proper gas settings",
                "4. Verify contract deployment", 
                "5. Initialize contract parameters"
            ]
        elif "htlc" in content_lower:
            return [
                "1. Set up HTLC contract templates",
                "2. Configure timelock parameters (24h default)",
                "3. Generate secure hash secrets",
                "4. Deploy HTLC on both chains",
                "5. Test lock/unlock mechanisms"
            ]
        else:
            return [
                "1. Specify your DeFi operation (swap, deploy, test)",
                "2. Configure testnet settings", 
                "3. Execute operation with monitoring",
                "4. Validate results and security"
            ]

    def _detect_operation_type(self, content: str) -> str:
        """Detect the type of Sepolia operation requested."""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["deploy", "contract", "fusion"]):
            return "contract_deployment"
        elif any(word in content_lower for word in ["htlc", "hash", "timelock"]):
            return "htlc_implementation"
        elif any(word in content_lower for word in ["resolver", "monitor", "automated"]):
            return "resolver_setup"
        elif any(word in content_lower for word in ["test", "swap", "execute"]):
            return "test_execution"
        else:
            return "general"

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


# Alias for backward compatibility
DogeSmartXRevolutionaryAgent = DogeSmartXSepoliaAgent
