"""
DogeSmartX Core Services

Core business logic services for DogeSmartX agent including swap management,
market data, and blockchain interactions.
"""

import asyncio
import hashlib
import secrets
import time
from typing import Dict, List, Optional, Tuple
from decimal import Decimal

from app.logger import logger
from .config import DogeSmartXConfig
from .exceptions import *
from .models import *


class SwapService:
    """Core service for managing cross-chain swaps."""
    
    def __init__(self, config: DogeSmartXConfig, state: AgentState):
        self.config = config
        self.state = state
    
    @handle_exception
    async def create_swap(self, 
                         direction: SwapDirection,
                         amount: Decimal,
                         enable_partial_fills: bool = True,
                         timelock_hours: Optional[int] = None) -> SwapOrder:
        """Create a new cross-chain swap order."""
        
        # Validate inputs
        self._validate_swap_params(direction, amount)
        
        # Generate security parameters
        secret = secrets.token_hex(32)
        secret_hash = hashlib.sha256(secret.encode()).hexdigest()
        swap_id = self._generate_swap_id(direction, amount)
        
        # Determine chains and tokens
        from_chain, to_chain, from_token, to_token = self._parse_direction(direction)
        
        # Calculate timelock expiry
        timelock_hours = timelock_hours or self.config.default_timelock_hours
        timelock_expiry = int(time.time()) + (timelock_hours * 3600)
        
        # Create swap order
        swap = SwapOrder(
            swap_id=swap_id,
            direction=direction,
            from_chain=from_chain,
            to_chain=to_chain,
            from_token=from_token,
            to_token=to_token,
            amount=amount,
            secret_hash=secret_hash,
            timelock_expiry=timelock_expiry,
            partial_fills_enabled=enable_partial_fills
        )
        
        # Add to state
        self.state.add_swap(swap)
        
        logger.info(f"🔒 Created swap {swap_id}: {amount} {from_token} → {to_token}")
        
        return swap
    
    @handle_exception
    async def execute_partial_fill(self, swap_id: str, fill_amount: Decimal) -> PartialFill:
        """Execute a partial fill for an existing swap."""
        
        swap = self.state.get_active_swap(swap_id)
        if not swap:
            raise SwapError("Swap not found", swap_id=swap_id)
        
        # Validate partial fill
        self._validate_partial_fill(swap, fill_amount)
        
        # Execute fill
        fill_id = f"{swap_id}_{int(time.time())}"
        fill = PartialFill(
            fill_id=fill_id,
            swap_id=swap_id,
            amount=fill_amount
        )
        
        # Update swap state
        new_filled = swap.filled_amount + fill_amount
        self.state.update_swap(swap_id, filled_amount=new_filled)
        
        # Update charity pool if enabled
        if self.config.charity_enabled:
            charity_amount = fill_amount * Decimal(str(self.config.charity_fee_percentage / 100))
            self.state.charity_pool += charity_amount
            
        logger.info(f"💰 Partial fill: {fill_amount} for swap {swap_id}")
        
        return fill
    
    @handle_exception
    async def check_timelock_status(self, swap_id: str) -> Dict[str, Any]:
        """Check timelock status for a swap."""
        
        swap = self.state.get_active_swap(swap_id)
        if not swap:
            raise SwapError("Swap not found", swap_id=swap_id)
        
        current_time = int(time.time())
        
        if swap.is_expired:
            # Update swap status if expired
            self.state.update_swap(swap_id, status=SwapStatus.EXPIRED)
            
            return {
                "expired": True,
                "refund_available": True,
                "message": "🕐 Timelock expired - refund available",
                "expired_hours": (current_time - swap.timelock_expiry) / 3600
            }
        else:
            return {
                "expired": False,
                "time_remaining_hours": swap.time_remaining_hours,
                "message": f"⏰ Timelock active - {swap.time_remaining_hours:.1f} hours remaining"
            }
    
    def _validate_swap_params(self, direction: SwapDirection, amount: Decimal) -> None:
        """Validate swap parameters."""
        if direction not in SwapDirection:
            raise InvalidSwapDirectionError(str(direction))
        
        if amount <= 0:
            raise ValidationError("Amount must be positive", field="amount", value=amount)
        
        if amount < Decimal(str(self.config.min_swap_amount)):
            raise ValidationError(
                f"Amount below minimum {self.config.min_swap_amount}",
                field="amount", value=amount
            )
        
        if amount > Decimal(str(self.config.max_swap_amount)):
            raise ValidationError(
                f"Amount exceeds maximum {self.config.max_swap_amount}",
                field="amount", value=amount
            )
    
    def _validate_partial_fill(self, swap: SwapOrder, fill_amount: Decimal) -> None:
        """Validate partial fill parameters."""
        if not swap.partial_fills_enabled:
            raise PartialFillError(
                "Partial fills not enabled for this swap",
                swap.swap_id, float(fill_amount), 0
            )
        
        if swap.is_expired:
            raise TimelockExpiredError(
                swap.swap_id, swap.timelock_expiry, int(time.time())
            )
        
        if swap.status not in [SwapStatus.PENDING, SwapStatus.PARTIALLY_FILLED]:
            raise PartialFillError(
                f"Cannot fill swap with status {swap.status}",
                swap.swap_id, float(fill_amount), 0
            )
        
        remaining = swap.remaining_amount
        if fill_amount > remaining:
            raise PartialFillError(
                "Fill amount exceeds remaining order size",
                swap.swap_id, float(fill_amount), float(remaining)
            )
    
    def _parse_direction(self, direction: SwapDirection) -> Tuple[NetworkType, NetworkType, str, str]:
        """Parse swap direction into chain and token information."""
        if direction == SwapDirection.ETH_TO_DOGE:
            return NetworkType.ETHEREUM, NetworkType.DOGECOIN, "ETH", "DOGE"
        elif direction == SwapDirection.DOGE_TO_ETH:
            return NetworkType.DOGECOIN, NetworkType.ETHEREUM, "DOGE", "ETH"
        else:
            raise InvalidSwapDirectionError(str(direction))
    
    def _generate_swap_id(self, direction: SwapDirection, amount: Decimal) -> str:
        """Generate unique swap ID."""
        timestamp = str(time.time())
        data = f"{direction}{amount}{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


class MarketService:
    """Service for managing market data and analysis."""
    
    def __init__(self, config: DogeSmartXConfig, state: AgentState):
        self.config = config
        self.state = state
    
    @handle_exception
    async def update_market_data(self, symbol: str, price: Decimal, 
                               source: str = "mock") -> MarketData:
        """Update market data for a symbol."""
        
        market_data = MarketData(
            symbol=symbol,
            price_usd=price,
            source=source
        )
        
        self.state.market_data[symbol] = market_data
        
        logger.info(f"📊 Updated market data: {symbol} = ${price}")
        
        return market_data
    
    @handle_exception
    async def get_swap_recommendation(self) -> Dict[str, Any]:
        """Generate swap timing recommendation based on market conditions."""
        
        doge_data = self.state.market_data.get("DOGE")
        eth_data = self.state.market_data.get("ETH")
        
        if not doge_data or not eth_data:
            return {
                "recommendation": "Gathering market data for optimal recommendations...",
                "confidence": "low"
            }
        
        # Simple recommendation logic based on gas fees
        gas_level = float(self.state.gas_fees.standard) if self.state.gas_fees else 50
        
        if gas_level < 30:
            recommendation = "🟢 OPTIMAL: Low gas fees detected - great time for swaps!"
            confidence = "high"
        elif gas_level < 50:
            recommendation = "🟡 MODERATE: Gas fees are reasonable for medium-sized swaps"
            confidence = "medium"
        else:
            recommendation = "🔴 HIGH: Consider waiting for lower gas fees unless urgent"
            confidence = "low"
        
        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "gas_level": gas_level,
            "doge_price": float(doge_data.price_usd),
            "eth_price": float(eth_data.price_usd),
            "timestamp": time.time()
        }
    
    @handle_exception
    async def update_gas_fees(self, slow: Decimal, standard: Decimal, 
                            fast: Decimal, instant: Decimal) -> GasFees:
        """Update current gas fee information."""
        
        gas_fees = GasFees(
            slow=slow,
            standard=standard,
            fast=fast,
            instant=instant
        )
        
        self.state.gas_fees = gas_fees
        
        logger.info(f"⛽ Updated gas fees: {standard} gwei (standard)")
        
        return gas_fees


class ContractService:
    """Service for managing smart contract interactions."""
    
    def __init__(self, config: DogeSmartXConfig):
        self.config = config
    
    @handle_exception
    async def check_deployment_status(self) -> Dict[str, Any]:
        """Check deployment status of required contracts."""
        
        status = {
            "ready_for_deployment": True,
            "contracts": {},
            "deployment_required": []
        }
        
        for name, contract_config in self.config.contracts.items():
            is_deployed = contract_config.is_deployed
            status["contracts"][name] = {
                "deployed": is_deployed,
                "address": contract_config.address if is_deployed else "Not deployed"
            }
            
            if not is_deployed:
                status["deployment_required"].append(name)
                status["ready_for_deployment"] = False
        
        return status
    
    @handle_exception
    async def prepare_deployment_config(self, network: NetworkType) -> Dict[str, Any]:
        """Prepare configuration for contract deployment."""
        
        try:
            network_config = self.config.get_network(network.value)
        except ValueError as e:
            raise NetworkError(f"Network configuration not found: {network}", network=network.value)
        
        deployment_config = {
            "network": network_config.name,
            "rpc_url": network_config.rpc_url,
            "chain_id": network_config.chain_id,
            "gas_limit": network_config.gas_limit,
            "gas_price_gwei": network_config.gas_price_gwei,
            "contracts_to_deploy": []
        }
        
        # Add contracts that need deployment
        for name, contract_config in self.config.contracts.items():
            if not contract_config.is_deployed:
                deployment_config["contracts_to_deploy"].append({
                    "name": name,
                    "abi_path": contract_config.abi_path
                })
        
        return deployment_config


class CommunityService:
    """Service for community features and sentiment analysis."""
    
    def __init__(self, config: DogeSmartXConfig, state: AgentState):
        self.config = config
        self.state = state
    
    @handle_exception
    async def update_sentiment(self, sentiment: str = None) -> str:
        """Update community sentiment."""
        
        if sentiment:
            self.state.community_sentiment = sentiment
        else:
            # Mock sentiment analysis - in real implementation would use APIs
            sentiments = [
                "🚀 TO THE MOON!",
                "📈 Bullish vibes", 
                "🐕 Much wow",
                "💎 Diamond hands",
                "🌕 Moon soon"
            ]
            import random
            self.state.community_sentiment = random.choice(sentiments)
        
        logger.info(f"🎭 Community sentiment: {self.state.community_sentiment}")
        
        return self.state.community_sentiment
    
    @handle_exception
    async def get_meme_interface_elements(self) -> List[str]:
        """Get meme interface elements for UI."""
        
        if not self.config.meme_mode:
            return []
        
        elements = [
            "🐕 Doge animations",
            "🚀 Rocket launch effects",
            "🌕 Moon phase indicators", 
            "💎 Diamond hand badges",
            "📈 Much gains counters",
            "🎭 Community sentiment display",
            "💝 Charity donation tracker"
        ]
        
        return elements
    
    @handle_exception
    async def calculate_charity_contribution(self, amount: Decimal) -> Decimal:
        """Calculate charity contribution for a transaction."""
        
        if not self.config.charity_enabled:
            return Decimal("0")
        
        contribution = amount * Decimal(str(self.config.charity_fee_percentage / 100))
        
        return contribution
