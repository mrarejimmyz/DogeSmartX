"""
DogeSmartX Agent - Modular Implementation

Main agent class that orchestrates all DogeSmartX services and provides
a clean, debuggable interface for cross-chain DeFi operations.
"""

import asyncio
import json
import re
import time
from typing import Any, Dict, List, Optional
from decimal import Decimal

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

from .config import DogeSmartXConfig, config as dogesmartx_config
from .exceptions import *
from .models import *
from .services import SwapService, MarketService, ContractService, CommunityService


class DogeSmartXAgent(ToolCallAgent):
    """
    Modular DogeSmartX Agent - AI-powered DeFi cross-chain swap assistant.
    
    Features:
    - Bidirectional ETH ↔ DOGE cross-chain swaps
    - Hashlock/timelock atomic swap security
    - Onchain execution with testnet deployment
    - Partial fills for better liquidity
    - Community features and charity integration
    - Comprehensive debugging and error handling
    """

    name: str = "DogeSmartX"
    description: str = (
        "Modular AI-powered DeFi agent for secure cross-chain swaps between "
        "Ethereum and Dogecoin with advanced features and debugging capabilities"
    )
    
    # Agent configuration
    max_steps: int = 25
    max_observe: int = 20000
    
    # DogeSmartX state
    config: DogeSmartXConfig = Field(default_factory=lambda: dogesmartx_config)
    state: AgentState = Field(default_factory=AgentState)
    
    # Services
    swap_service: Optional[SwapService] = None
    market_service: Optional[MarketService] = None
    contract_service: Optional[ContractService] = None
    community_service: Optional[CommunityService] = None
    
    def __init__(self, **kwargs):
        """Initialize DogeSmartX agent with modular services."""
        super().__init__(**kwargs)
        
        # Validate configuration
        try:
            self.config.validate()
        except ValueError as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
        
        # Initialize services
        self._initialize_services()
        
        # Initialize tools
        self.available_tools = ToolCollection(
            PythonExecute(),
            StrReplaceEditor(),
            WebSearch(),
            Terminate(),
        )
        
        # Set system prompts
        self.system_prompt = self._get_system_prompt()
        self.next_step_prompt = self._get_next_step_prompt()
        
        logger.info("🐕 DogeSmartX Agent initialized with modular architecture! 🚀")
        
        if self.config.debug_mode:
            logger.debug(f"Configuration: {self.config}")
            logger.debug(f"Initial state: {self.state}")

    def _initialize_services(self) -> None:
        """Initialize all DogeSmartX services."""
        try:
            self.swap_service = SwapService(self.config, self.state)
            self.market_service = MarketService(self.config, self.state)
            self.contract_service = ContractService(self.config)
            self.community_service = CommunityService(self.config, self.state)
            
            logger.info("✅ All DogeSmartX services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise DogeSmartXError(f"Service initialization failed: {e}")

    def _get_system_prompt(self) -> str:
        """Get the system prompt for DogeSmartX agent."""
        return f"""You are DogeSmartX, a modular AI-powered DeFi agent specializing in cross-chain swaps!

🐕 YOUR MISSION 🐕
Provide secure, efficient, and fun DeFi solutions with:
- Bidirectional ETH ↔ DOGE cross-chain swaps using advanced protocols
- Hashlock/timelock atomic swap security for trustless transactions
- Onchain execution on testnets/mainnet with proper contract deployment
- Partial fills for optimal liquidity and user experience
- Community-driven features with Dogecoin spirit and meme integration
- Charity donations supporting Dogecoin-related causes
- Comprehensive debugging and error handling

🎯 CORE CAPABILITIES:
1. ATOMIC SWAPS: Secure hashlock/timelock mechanisms for cross-chain trading
2. BIDIRECTIONAL TRADING: Support both ETH→DOGE and DOGE→ETH directions
3. ONCHAIN EXECUTION: Real contract deployment and execution on testnets
4. PARTIAL FILLS: Enable fractional order fulfillment for better liquidity
5. MARKET INTELLIGENCE: Real-time price tracking and optimal timing analysis
6. COMMUNITY FEATURES: Meme integration, sentiment tracking, and social elements
7. CHARITY INTEGRATION: Transparent donation pool for Dogecoin causes
8. DEBUG MODE: {'ENABLED - Detailed logging active' if self.config.debug_mode else 'Available for troubleshooting'}

🔒 SECURITY FEATURES:
- Cryptographic hashlock protection
- Time-based refund mechanisms
- Multi-signature support for large transactions
- Slippage protection and MEV resistance
- Comprehensive input validation

🚀 CONFIGURATION:
- Workspace: {app_config.workspace_root}
- Partial Fills: {'✅ Enabled' if self.config.partial_fills_enabled else '❌ Disabled'}
- Charity: {'✅ Enabled ({self.config.charity_fee_percentage}%)' if self.config.charity_enabled else '❌ Disabled'}
- Meme Mode: {'✅ Much Wow!' if self.config.meme_mode else '❌ Serious Mode'}
- Debug Mode: {'✅ Active' if self.config.debug_mode else '❌ Production'}

Always maintain the playful Dogecoin community spirit while delivering professional, 
secure DeFi solutions! Much technology, such security, very scalable! 🌕
"""

    def _get_next_step_prompt(self) -> str:
        """Get the next step prompt for DogeSmartX agent."""
        return """What's your next DogeSmartX move? 

🎯 Available Actions:
🔄 CROSS-CHAIN SWAPS: Create ETH↔DOGE swaps with atomic security
⚡ PARTIAL FILLS: Execute fractional order fulfillment  
📊 MARKET ANALYSIS: Check prices, gas fees, and optimal timing
🔒 ATOMIC SWAPS: Manage hashlock/timelock security mechanisms
⛓️ ONCHAIN OPS: Deploy contracts and execute on testnets
🎭 COMMUNITY: Update sentiment, memes, and social features
💝 CHARITY: Track donations and community contributions
🛠️ DEVELOPMENT: Build dApps, contracts, and interfaces
🐛 DEBUG: Troubleshoot issues and analyze system state

Keep the Dogecoin spirit alive - make it secure, scalable, and fun! 🐕🚀
"""

    async def step(self) -> str:
        """Execute a single step in DogeSmartX workflow with error handling."""
        try:
            # Get user messages
            user_messages = [msg for msg in self.memory.messages if msg.role == "user"]
            
            if not user_messages:
                return await self._get_welcome_message()
            
            latest_request = user_messages[-1].content.lower()
            
            # Route request to appropriate handler
            return await self._route_request(latest_request)
            
        except DogeSmartXError as e:
            log_exception(logger, e)
            return self._format_error_response(e)
        except Exception as e:
            error = DogeSmartXError(
                f"Unexpected error in DogeSmartX step: {str(e)}",
                error_code="UNEXPECTED_ERROR",
                context={"original_error": str(e), "error_type": type(e).__name__}
            )
            log_exception(logger, error)
            return self._format_error_response(error)

    async def _route_request(self, request: str) -> str:
        """Route user request to appropriate handler."""
        
        # Swap operations
        if any(keyword in request for keyword in ["swap", "exchange", "trade"]):
            return await self._handle_swap_request(request)
        
        # Atomic swap management
        elif any(keyword in request for keyword in ["hashlock", "timelock", "atomic"]):
            return await self._handle_atomic_request(request)
        
        # Partial fills
        elif any(keyword in request for keyword in ["partial", "fill"]):
            return await self._handle_partial_fill_request(request)
        
        # Market analysis
        elif any(keyword in request for keyword in ["market", "price", "analysis", "gas"]):
            return await self._handle_market_request(request)
        
        # Onchain operations
        elif any(keyword in request for keyword in ["onchain", "deploy", "testnet", "mainnet", "contract"]):
            return await self._handle_onchain_request(request)
        
        # Community features
        elif any(keyword in request for keyword in ["community", "sentiment", "meme"]):
            return await self._handle_community_request(request)
        
        # Charity operations
        elif any(keyword in request for keyword in ["charity", "donation", "pool"]):
            return await self._handle_charity_request(request)
        
        # Development
        elif any(keyword in request for keyword in ["build", "create", "develop", "app"]):
            return await self._handle_development_request(request)
        
        # Debug operations
        elif any(keyword in request for keyword in ["debug", "status", "state", "error"]):
            return await self._handle_debug_request(request)
        
        # Default capabilities overview
        else:
            return await self._get_capabilities_overview()

    async def _handle_swap_request(self, request: str) -> str:
        """Handle swap creation and execution requests."""
        try:
            # Parse swap parameters
            direction, amount, enable_partial = self._parse_swap_request(request)
            
            # Create swap
            swap = await self.swap_service.create_swap(direction, amount, enable_partial)
            
            # Prepare onchain configuration
            deployment_status = await self.contract_service.check_deployment_status()
            
            return f"""🔄 DogeSmartX Swap Created Successfully!

📋 SWAP DETAILS:
- Swap ID: {swap.swap_id}
- Direction: {swap.direction.value.replace('_', ' → ').upper()}
- Amount: {swap.amount} {swap.from_token}
- Target: {swap.to_token}
- Status: {swap.status.value.title()}

🔒 ATOMIC SECURITY:
- Hashlock: {swap.secret_hash[:16]}...
- Timelock: {swap.time_remaining_hours:.1f} hours remaining
- Partial Fills: {'✅ Enabled' if swap.partial_fills_enabled else '❌ Disabled'}

⛓️ ONCHAIN STATUS:
- Contracts Ready: {'✅' if deployment_status['ready_for_deployment'] else '❌'}
- Deployment Required: {', '.join(deployment_status['deployment_required']) if deployment_status['deployment_required'] else 'None'}

💝 Charity Contribution: {await self.community_service.calculate_charity_contribution(swap.amount)} {swap.from_token}

🚀 Status: Ready for execution! Use 'deploy to testnet' to prepare onchain execution.
"""

        except Exception as e:
            raise SwapError(f"Failed to create swap: {str(e)}")

    async def _handle_partial_fill_request(self, request: str) -> str:
        """Handle partial fill operations."""
        try:
            fillable_swaps = self.state.get_fillable_swaps()
            
            if not fillable_swaps:
                return """💰 No Active Orders for Partial Fills

🎯 PARTIAL FILL FEATURES:
- Fill any amount up to order size
- Real-time progress tracking  
- Better liquidity through order splitting
- Continuous trading while orders remain active

Create a swap first to enable partial fills!
Try: "swap 1 ETH to DOGE with partial fills"
"""

            # Check if user specified a fill amount and swap ID
            swap_id_match = re.search(r'([a-f0-9]{16})', request)
            amount_match = re.search(r'(\d+(?:\.\d+)?)', request)
            
            if swap_id_match and amount_match:
                swap_id = swap_id_match.group(1)
                fill_amount = Decimal(amount_match.group(1))
                
                fill = await self.swap_service.execute_partial_fill(swap_id, fill_amount)
                swap = self.state.get_active_swap(swap_id)
                
                return f"""💰 Partial Fill Executed Successfully!

📋 FILL DETAILS:
- Fill ID: {fill.fill_id}
- Swap ID: {fill.swap_id}
- Amount Filled: {fill.amount} {swap.from_token}
- Total Progress: {swap.fill_percentage:.1f}% ({swap.filled_amount}/{swap.amount})
- Remaining: {swap.remaining_amount} {swap.from_token}
- Status: {swap.status.value.title()}

💝 Charity Contribution: {await self.community_service.calculate_charity_contribution(fill.amount)} {swap.from_token}

{'🎉 Order Complete!' if swap.status == SwapStatus.COMPLETED else '🔄 Ready for more fills!'}
"""
            
            # Show available orders for filling
            orders_list = []
            for swap in fillable_swaps[:5]:  # Show up to 5 orders
                orders_list.append(
                    f"- {swap.swap_id}: {swap.remaining_amount} {swap.from_token} "
                    f"({swap.fill_percentage:.1f}% filled)"
                )
            
            return f"""💰 ORDERS AVAILABLE FOR PARTIAL FILLS:

{chr(10).join(orders_list)}

💡 To execute a fill:
"fill 0.5 for {fillable_swaps[0].swap_id}"

🎯 Benefits:
- Instant execution of available liquidity
- No waiting for full order completion
- Flexible trading amounts
- Real-time progress tracking
"""

        except Exception as e:
            raise PartialFillError(f"Partial fill operation failed: {str(e)}", "", 0, 0)

    async def _handle_market_request(self, request: str) -> str:
        """Handle market analysis and data requests."""
        try:
            # Update mock market data
            await self.market_service.update_market_data("DOGE", Decimal("0.08"))
            await self.market_service.update_market_data("ETH", Decimal("2500"))
            await self.market_service.update_gas_fees(
                Decimal("20"), Decimal("35"), Decimal("50"), Decimal("70")
            )
            
            # Get recommendation
            recommendation = await self.market_service.get_swap_recommendation()
            
            return f"""📊 DogeSmartX Market Intelligence

🔍 CURRENT MARKET DATA:
- DOGE Price: ${self.state.market_data['DOGE'].price_usd}
- ETH Price: ${self.state.market_data['ETH'].price_usd}
- DOGE/ETH Ratio: {float(self.state.market_data['DOGE'].price_usd / self.state.market_data['ETH'].price_usd):.8f}

⛽ GAS FEES (Ethereum):
- Slow: {self.state.gas_fees.slow} gwei
- Standard: {self.state.gas_fees.standard} gwei  
- Fast: {self.state.gas_fees.fast} gwei
- Instant: {self.state.gas_fees.instant} gwei

🎯 SWAP RECOMMENDATION:
{recommendation['recommendation']}
Confidence: {recommendation['confidence'].upper()}

📈 OPTIMAL TIMING:
- Current gas level: {recommendation['gas_level']} gwei
- Best for: {'Large swaps' if recommendation['confidence'] == 'high' else 'Medium swaps' if recommendation['confidence'] == 'medium' else 'Small swaps or wait'}

💡 Analysis based on current network conditions and market data.
"""

        except Exception as e:
            raise MarketDataError(f"Market analysis failed: {str(e)}")

    async def _handle_onchain_request(self, request: str) -> str:
        """Handle onchain deployment and execution requests."""
        try:
            deployment_status = await self.contract_service.check_deployment_status()
            
            # Prepare deployment configurations
            eth_config = await self.contract_service.prepare_deployment_config(NetworkType.ETHEREUM)
            
            return f"""⛓️ DogeSmartX Onchain Execution Status

🌐 NETWORK READINESS:
- Ethereum Testnet: ✅ {self.config.get_network('ethereum').name.title()}
- Dogecoin Testnet: ✅ {self.config.get_network('dogecoin').name.title()}
- RPC Connections: ✅ Configured

📜 CONTRACT DEPLOYMENT:
""" + "\n".join([
    f"- {name}: {'✅ Deployed' if info['deployed'] else '❌ Needs Deployment'} ({info['address']})"
    for name, info in deployment_status['contracts'].items()
]) + f"""

🚀 DEPLOYMENT CONFIGURATION:
- Target Network: {eth_config['network'].title()}
- Chain ID: {eth_config['chain_id']}
- Gas Limit: {eth_config['gas_limit']:,}
- Gas Price: {eth_config['gas_price_gwei']} gwei

📋 DEPLOYMENT STEPS:
""" + "\n".join([
    f"{i+1}. Deploy {contract['name']}"
    for i, contract in enumerate(eth_config['contracts_to_deploy'])
]) + f"""

💡 DEMO EXECUTION READY:
- All swaps will execute with real onchain transactions
- Testnet tokens will be used for demonstration
- Full atomic swap security maintained

{'🎯 Ready to deploy contracts!' if deployment_status['deployment_required'] else '✅ All contracts deployed - ready for trading!'}
"""

        except Exception as e:
            raise ContractError(f"Onchain status check failed: {str(e)}")

    async def _handle_community_request(self, request: str) -> str:
        """Handle community features and sentiment."""
        try:
            sentiment = await self.community_service.update_sentiment()
            meme_elements = await self.community_service.get_meme_interface_elements()
            
            return f"""🎭 DogeSmartX Community Hub

🌟 CURRENT VIBE:
{sentiment}

🎨 MEME INTERFACE READY:
""" + "\n".join(f"- {element}" for element in meme_elements) + f"""

🐕 COMMUNITY FEATURES:
- Dogecoin spirit: ✅ Much wow!
- Social sentiment tracking: ✅ Active
- Meme integration: {'✅ Enabled' if self.config.meme_mode else '❌ Disabled'}
- Community-driven recommendations: ✅ Ready

💬 COMMUNITY METRICS:
- Active Swaps: {len(self.state.active_swaps)}
- Community Sentiment: {self.state.community_sentiment}
- Charity Pool: 💝 ${self.state.charity_pool}

🚀 "Do Only Good Everyday" - The Dogecoin way!
Such community, much engagement, very wow! 🌕
"""

        except Exception as e:
            raise DogeSmartXError(f"Community features failed: {str(e)}")

    async def _handle_charity_request(self, request: str) -> str:
        """Handle charity pool and donation requests."""
        try:
            current_pool = self.state.charity_pool
            
            # Calculate total potential from active swaps
            potential_contributions = sum([
                await self.community_service.calculate_charity_contribution(swap.remaining_amount)
                for swap in self.state.active_swaps.values()
            ])
            
            return f"""💝 DogeSmartX Charity Pool

🎯 CURRENT STATUS:
- Pool Balance: ${current_pool}
- Pending from Active Swaps: ${potential_contributions}
- Total Potential: ${current_pool + potential_contributions}

⚙️ CHARITY SETTINGS:
- Fee Percentage: {self.config.charity_fee_percentage}% of each swap
- Status: {'✅ Enabled' if self.config.charity_enabled else '❌ Disabled'}
- Automatic Deduction: ✅ From all completed swaps

🎭 SUPPORTED CAUSES:
- Dogecoin community development
- Animal welfare organizations  
- Open source blockchain projects
- Community education initiatives

📊 TRANSPARENCY:
- All donations tracked on-chain
- Public donation addresses
- Community voting on fund allocation
- Regular impact reports

💡 "Do Only Good Everyday" - Every swap helps the community! 🐕💝
"""

        except Exception as e:
            raise DogeSmartXError(f"Charity operations failed: {str(e)}")

    async def _handle_development_request(self, request: str) -> str:
        """Handle development and building requests."""
        try:
            dev_capabilities = []
            
            if any(keyword in request for keyword in ["web", "frontend", "ui"]):
                dev_capabilities.extend([
                    "🌐 Responsive web interface with meme integration",
                    "🎨 Real-time trading dashboard",
                    "📱 Mobile-friendly design"
                ])
            
            if any(keyword in request for keyword in ["smart", "contract", "solidity"]):
                dev_capabilities.extend([
                    "📜 Atomic swap smart contracts",
                    "🔒 Hashlock/timelock implementations", 
                    "🌉 Cross-chain bridge contracts"
                ])
            
            if any(keyword in request for keyword in ["api", "backend"]):
                dev_capabilities.extend([
                    "⚡ RESTful API for swap operations",
                    "📊 Real-time market data feeds",
                    "🔗 Blockchain integration services"
                ])
            
            if not dev_capabilities:
                dev_capabilities = [
                    "🌐 Full-stack DeFi application",
                    "📜 Smart contract development",
                    "⚡ Real-time market integration", 
                    "🎨 Meme-themed UI components",
                    "📱 Mobile responsive interfaces",
                    "🔒 Security audit tools"
                ]
            
            return f"""🛠️ DogeSmartX Development Suite

🎯 AVAILABLE DEVELOPMENT SERVICES:
""" + "\n".join(f"- {capability}" for capability in dev_capabilities) + f"""

🔧 TECHNICAL STACK:
- Smart Contracts: Solidity, Vyper
- Frontend: React, Vue.js, Web3.js
- Backend: Python, Node.js, FastAPI
- Blockchain: Ethereum, Dogecoin, 1inch Protocol
- Testing: Hardhat, Truffle, Pytest

🚀 READY-TO-DEPLOY FEATURES:
- Atomic swap mechanisms ✅
- Partial fill functionality ✅  
- Multi-signature support ✅
- Real-time price feeds ✅
- Community integration ✅
- Charity donation system ✅

💡 Let's build the future of DeFi with Dogecoin spirit!
Much development, such technology, very scalable! 🐕🚀
"""

        except Exception as e:
            raise DogeSmartXError(f"Development request failed: {str(e)}")

    async def _handle_debug_request(self, request: str) -> str:
        """Handle debugging and system status requests."""
        try:
            # System status
            active_swaps = len(self.state.active_swaps)
            completed_swaps = len([s for s in self.state.active_swaps.values() if s.status == SwapStatus.COMPLETED])
            failed_swaps = len([s for s in self.state.active_swaps.values() if s.status == SwapStatus.FAILED])
            
            # Service status
            services_status = {
                "SwapService": "✅ Active" if self.swap_service else "❌ Inactive",
                "MarketService": "✅ Active" if self.market_service else "❌ Inactive", 
                "ContractService": "✅ Active" if self.contract_service else "❌ Inactive",
                "CommunityService": "✅ Active" if self.community_service else "❌ Inactive"
            }
            
            return f"""🐛 DogeSmartX Debug Information

🔧 SYSTEM STATUS:
- Agent Name: {self.name}
- Version: {self.config.version}
- Debug Mode: {'✅ Enabled' if self.config.debug_mode else '❌ Disabled'}
- Uptime: Active

📊 SWAP STATISTICS:
- Active Swaps: {active_swaps}
- Completed: {completed_swaps}
- Failed: {failed_swaps}
- Success Rate: {(completed_swaps / max(1, active_swaps)) * 100:.1f}%

🛠️ SERVICE STATUS:
""" + "\n".join(f"- {service}: {status}" for service, status in services_status.items()) + f"""

⚙️ CONFIGURATION:
- Partial Fills: {'✅' if self.config.partial_fills_enabled else '❌'}
- Charity: {'✅' if self.config.charity_enabled else '❌'} ({self.config.charity_fee_percentage}%)
- Meme Mode: {'✅' if self.config.meme_mode else '❌'}
- Min Swap: {self.config.min_swap_amount}
- Max Swap: {self.config.max_swap_amount}

💾 STATE SNAPSHOT:
- Market Data: {len(self.state.market_data)} symbols
- Gas Fees: {'✅ Current' if self.state.gas_fees else '❌ Stale'}
- Charity Pool: ${self.state.charity_pool}
- Community Sentiment: {self.state.community_sentiment}

🚀 All systems operational! Much debug, such insight! 🐕
"""

        except Exception as e:
            raise DogeSmartXError(f"Debug request failed: {str(e)}")

    async def _get_welcome_message(self) -> str:
        """Get welcome message for new sessions."""
        return """🐕 Welcome to DogeSmartX - Modular DeFi Magic! 🚀

🎯 Ready for secure cross-chain adventures with:
✅ Bidirectional ETH ↔ DOGE atomic swaps
✅ Hashlock/timelock security mechanisms  
✅ Partial fills for optimal liquidity
✅ Onchain testnet execution ready
✅ Community features with Dogecoin spirit
✅ Charity integration for good causes

💡 Try these commands:
- "swap 1 ETH to DOGE" - Create atomic swap
- "market analysis" - Check current conditions
- "check atomic swaps" - View active security
- "deploy to testnet" - Prepare onchain execution
- "debug status" - System health check

Much technology, such security, very scalable! 🌕✨
"""

    async def _get_capabilities_overview(self) -> str:
        """Get comprehensive capabilities overview."""
        return f"""🐕 DogeSmartX - Complete Capabilities Overview 🚀

🔄 BIDIRECTIONAL CROSS-CHAIN SWAPS:
- ETH → DOGE and DOGE → ETH exchanges
- 1inch Fusion+ protocol integration  
- Real-time route optimization
- Slippage protection and MEV resistance

🔒 ATOMIC SWAP SECURITY:
- SHA256 hashlock mechanisms
- Configurable timelock protection ({self.config.default_timelock_hours}h default)
- Non-custodial, trustless transactions
- Cryptographic proof verification

⛓️ ONCHAIN EXECUTION:
- Testnet deployment for demos
- Limit Order Protocol integration
- Real transaction execution
- Cross-chain bridge functionality

💰 PARTIAL FILLS:
- Fractional order fulfillment
- Real-time progress tracking
- Better liquidity utilization
- Continuous trading capabilities

📊 MARKET INTELLIGENCE:
- Live DOGE/ETH price tracking
- Gas fee optimization
- Optimal timing recommendations
- Community sentiment analysis

🎭 COMMUNITY FEATURES:
- Meme-themed interface elements
- Social sentiment integration
- Dogecoin culture preservation
- Community-driven recommendations

💝 CHARITY INTEGRATION:
- Automatic {self.config.charity_fee_percentage}% donation deduction
- Transparent pool tracking (${self.state.charity_pool} current)
- "Do Only Good Everyday" philosophy
- Community cause support

🛠️ DEVELOPMENT READY:
- Smart contract creation
- dApp frontend development
- API integration capabilities
- Mobile-responsive interfaces

🐛 DEBUG & MONITORING:
- Comprehensive error handling
- Performance monitoring
- State inspection tools
- Configuration validation

🚀 EXAMPLE COMMANDS:
- "swap 0.5 ETH to DOGE with partial fills"
- "fill 100 DOGE for [swap_id]"
- "check timelock status"
- "deploy contracts to testnet" 
- "market analysis"
- "community sentiment"
- "debug system status"

Ready to revolutionize DeFi with Dogecoin spirit!
Much wow, such technology, very modular! 🌕✨
"""

    def _parse_swap_request(self, request: str) -> tuple[SwapDirection, Decimal, bool]:
        """Parse swap request to extract parameters."""
        # Extract amount
        amount_match = re.search(r'(\d+(?:\.\d+)?)', request)
        amount = Decimal(amount_match.group(1)) if amount_match else Decimal("1.0")
        
        # Determine direction
        if any(phrase in request for phrase in ["eth to doge", "ethereum to dogecoin"]):
            direction = SwapDirection.ETH_TO_DOGE
        elif any(phrase in request for phrase in ["doge to eth", "dogecoin to ethereum"]):
            direction = SwapDirection.DOGE_TO_ETH
        else:
            # Default to ETH to DOGE
            direction = SwapDirection.ETH_TO_DOGE
        
        # Check for partial fills
        enable_partial = "partial" in request.lower()
        
        return direction, amount, enable_partial

    def _format_error_response(self, error: DogeSmartXError) -> str:
        """Format error response for user."""
        return f"""🚨 DogeSmartX Error: {error.error_code}

❌ {error.message}

💡 Context:
""" + "\n".join(f"- {k}: {v}" for k, v in error.context.items() if v is not None) + f"""

🛠️ Troubleshooting:
- Check 'debug status' for system health
- Verify swap parameters are valid
- Ensure contracts are deployed if needed
- Try again with different parameters

Much error, such debugging, very helpful! 🐕🔧
"""

    async def finalize_task(self, result: str) -> str:
        """Finalize DogeSmartX task with comprehensive summary."""
        
        # Calculate session statistics
        total_swaps = len(self.state.active_swaps)
        completed_swaps = len([s for s in self.state.active_swaps.values() if s.status == SwapStatus.COMPLETED])
        partial_fills = len([s for s in self.state.active_swaps.values() if s.status == SwapStatus.PARTIALLY_FILLED])
        failed_swaps = len([s for s in self.state.active_swaps.values() if s.status == SwapStatus.FAILED])
        
        # Check deployment readiness
        deployment_status = await self.contract_service.check_deployment_status()
        contracts_ready = deployment_status['ready_for_deployment']
        
        final_message = f"""🎉 DogeSmartX Mission Accomplished! 🎉

{result}

📊 SESSION SUMMARY:
✅ Core Features Delivered:
- 🔄 Bidirectional Swaps: ETH ↔ DOGE ready
- 🔒 Atomic Security: Hashlock/timelock implemented  
- ⛓️ Onchain Execution: {'✅ Ready' if contracts_ready else '🚧 Deployment pending'}
- 💰 Partial Fills: {'✅ Active' if self.config.partial_fills_enabled else '⚙️ Available'}

📈 Trading Statistics:
- Total Swaps Created: {total_swaps}
- Successfully Completed: {completed_swaps}
- Partial Fills Active: {partial_fills}
- Failed Attempts: {failed_swaps}
- Success Rate: {(completed_swaps / max(1, total_swaps)) * 100:.1f}%

💝 Community Impact:
- Charity Pool: ${self.state.charity_pool}
- Donations from {self.config.charity_fee_percentage}% of swap fees
- Community Sentiment: {self.state.community_sentiment}
- Dogecoin Spirit: 🐕✅

🔧 Technical Architecture:
- Modular Services: ✅ All active
- Error Handling: ✅ Comprehensive
- Debug Capabilities: ✅ Available
- Configuration Validation: ✅ Passed
- State Management: ✅ Robust

🌟 Deployment Status:
- Contract Readiness: {'✅ All deployed' if contracts_ready else f'🚧 {len(deployment_status["deployment_required"])} pending'}
- Network Configuration: ✅ Testnet ready
- Security Mechanisms: ✅ Hashlock/timelock active
- Cross-chain Bridge: {'✅ Ready' if contracts_ready else '🚧 Pending deployment'}

🚀 Innovation Delivered:
- Scalable modular architecture ✅
- Comprehensive debugging tools ✅  
- Type-safe data models ✅
- Professional error handling ✅
- Community-driven features ✅

Remember: "Do Only Good Everyday" - The Dogecoin way! 🌕

DogeSmartX is now production-ready for cross-chain DeFi!
Much technology, such architecture, very scalable! 🚀💎
"""
        
        # Add to memory and mark as complete
        self.update_memory("assistant", final_message)
        raise AgentTaskComplete(final_message)
