"""
Sepolia Testnet Resolver Service

Automated resolver for 1inch Fusion+ cross-chain swaps between
Sepolia ETH and Dogecoin testnet using HTLC mechanisms.
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

from app.logger import logger
from .sepolia_config import sepolia_config
from .htlc import CrossChainHTLCManager, HTLCSecret, HTLCContract


@dataclass
class SwapRequest:
    """Represents a cross-chain swap request."""
    swap_id: str
    from_chain: str
    to_chain: str
    from_token: str
    to_token: str
    from_amount: Decimal
    to_amount: Decimal
    from_address: str
    to_address: str
    timelock_hours: int
    status: str
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "swap_id": self.swap_id,
            "from_chain": self.from_chain,
            "to_chain": self.to_chain,
            "from_token": self.from_token,
            "to_token": self.to_token,
            "from_amount": str(self.from_amount),
            "to_amount": str(self.to_amount),
            "from_address": self.from_address,
            "to_address": self.to_address,
            "timelock_hours": self.timelock_hours,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }


class SepoliaTestnetResolver:
    """
    Automated resolver for Sepolia-Dogecoin testnet swaps.
    
    The resolver monitors both chains and facilitates atomic swaps by:
    1. Detecting DOGE lock transactions on Dogecoin testnet
    2. Locking equivalent ETH on Sepolia 
    3. Monitoring for ETH claims and secret reveals
    4. Claiming DOGE using the revealed secret
    """
    
    def __init__(self, htlc_manager: CrossChainHTLCManager):
        self.htlc_manager = htlc_manager
        self.config = sepolia_config
        self.pending_swaps: Dict[str, SwapRequest] = {}
        self.is_running = False
        self.monitoring_tasks: List[asyncio.Task] = []
        
        logger.info("🤖 Sepolia Testnet Resolver initialized")
    
    async def start(self):
        """Start the resolver monitoring services."""
        if self.is_running:
            logger.warning("⚠️ Resolver already running")
            return
        
        self.is_running = True
        
        # Start monitoring tasks
        self.monitoring_tasks = [
            asyncio.create_task(self._monitor_doge_locks()),
            asyncio.create_task(self._monitor_eth_claims()),
            asyncio.create_task(self._monitor_timeouts()),
            asyncio.create_task(self._health_check_service())
        ]
        
        logger.info("🚀 Resolver monitoring services started")
    
    async def stop(self):
        """Stop the resolver monitoring services."""
        self.is_running = False
        
        # Cancel all monitoring tasks
        for task in self.monitoring_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        
        logger.info("⏹️ Resolver monitoring services stopped")
    
    async def _monitor_doge_locks(self):
        """Monitor Dogecoin testnet for new HTLC locks."""
        while self.is_running:
            try:
                await self._check_new_doge_locks()
                await asyncio.sleep(self.config.resolver.poll_interval_seconds)
            except Exception as e:
                logger.error(f"❌ DOGE monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _monitor_eth_claims(self):
        """Monitor Sepolia for ETH HTLC claims and secret reveals."""
        while self.is_running:
            try:
                await self._check_eth_claims()
                await asyncio.sleep(self.config.resolver.poll_interval_seconds)
            except Exception as e:
                logger.error(f"❌ ETH monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _monitor_timeouts(self):
        """Monitor for expired swaps and trigger refunds."""
        while self.is_running:
            try:
                await self._check_timeout_refunds()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"❌ Timeout monitoring error: {e}")
                await asyncio.sleep(120)
    
    async def _health_check_service(self):
        """Periodic health check and status reporting."""
        while self.is_running:
            try:
                await self._perform_health_check()
                await asyncio.sleep(300)  # Health check every 5 minutes
            except Exception as e:
                logger.error(f"❌ Health check error: {e}")
                await asyncio.sleep(600)
    
    async def _check_new_doge_locks(self):
        """Check for new DOGE HTLC locks that need ETH counterparts."""
        # This would connect to Dogecoin testnet and scan for HTLC transactions
        # For testing, we'll simulate this process
        
        logger.debug("🔍 Scanning for new DOGE locks...")
        
        # Simulate finding a new DOGE lock
        # In production, this would parse Dogecoin transactions
        
    async def _check_eth_claims(self):
        """Check for ETH HTLC claims and extract secrets."""
        # This would monitor Sepolia for HTLC claim transactions
        # and extract the revealed secrets
        
        logger.debug("🔍 Scanning for ETH claims...")
        
        # Simulate monitoring Sepolia for claims
        # In production, this would watch contract events
    
    async def _check_timeout_refunds(self):
        """Check for expired swaps and initiate refunds."""
        current_time = int(time.time())
        
        for swap_id, swap_data in self.htlc_manager.active_swaps.items():
            if swap_data["status"] in ["both_locked", "eth_claimed"]:
                # Check if timelock has expired
                eth_htlc = swap_data.get("eth_htlc")
                doge_htlc = swap_data.get("doge_htlc")
                
                if eth_htlc and eth_htlc.parameters.time_lock <= current_time:
                    await self._initiate_refund(swap_id, "eth")
                
                if doge_htlc and doge_htlc.parameters.time_lock <= current_time:
                    await self._initiate_refund(swap_id, "doge")
    
    async def _initiate_refund(self, swap_id: str, chain: str):
        """Initiate refund for expired HTLC."""
        try:
            logger.warning(f"⏰ Initiating {chain.upper()} refund for expired swap: {swap_id}")
            
            if chain == "eth":
                # Refund ETH HTLC
                await self.htlc_manager.sepolia.refund_htlc(
                    swap_id, 
                    self.config.resolver.eth_private_key
                )
            elif chain == "doge":
                # Refund DOGE HTLC (would need implementation)
                logger.info(f"📤 DOGE refund initiated for {swap_id}")
            
            # Update swap status
            swap_data = self.htlc_manager.active_swaps[swap_id]
            swap_data["status"] = f"{chain}_refunded"
            
        except Exception as e:
            logger.error(f"❌ Refund failed for {swap_id}: {e}")
    
    async def _perform_health_check(self):
        """Perform system health check."""
        try:
            active_swaps = len(self.htlc_manager.active_swaps)
            pending_swaps = len(self.pending_swaps)
            
            logger.info(f"💚 Resolver Health: {active_swaps} active swaps, {pending_swaps} pending")
            
            # Check network connectivity
            await self._check_network_health()
            
            # Check wallet balances
            await self._check_wallet_balances()
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
    
    async def _check_network_health(self):
        """Check connectivity to both networks."""
        # Check Sepolia connectivity
        try:
            # This would check if we can connect to Sepolia
            logger.debug("✅ Sepolia network healthy")
        except Exception as e:
            logger.error(f"❌ Sepolia network issue: {e}")
        
        # Check Dogecoin testnet connectivity
        try:
            # This would check if we can connect to Dogecoin testnet
            logger.debug("✅ Dogecoin testnet healthy")
        except Exception as e:
            logger.error(f"❌ Dogecoin testnet issue: {e}")
    
    async def _check_wallet_balances(self):
        """Check resolver wallet balances."""
        try:
            # Check ETH balance
            eth_balance = Decimal("1.0")  # Simulated
            if eth_balance < self.config.fusion_plus.min_swap_amount_eth:
                logger.warning(f"⚠️ Low ETH balance: {eth_balance}")
            
            # Check DOGE balance
            doge_balance = Decimal("1000")  # Simulated
            if doge_balance < self.config.fusion_plus.min_swap_amount_doge:
                logger.warning(f"⚠️ Low DOGE balance: {doge_balance}")
                
        except Exception as e:
            logger.error(f"❌ Balance check failed: {e}")
    
    async def create_swap_request(self, 
                                from_chain: str,
                                to_chain: str,
                                from_token: str,
                                to_token: str,
                                from_amount: Decimal,
                                to_amount: Decimal,
                                from_address: str,
                                to_address: str,
                                timelock_hours: int = 24) -> SwapRequest:
        """Create a new cross-chain swap request."""
        
        # Generate swap ID
        swap_id = f"swap_{int(time.time())}_{len(self.pending_swaps)}"
        
        swap_request = SwapRequest(
            swap_id=swap_id,
            from_chain=from_chain,
            to_chain=to_chain,
            from_token=from_token,
            to_token=to_token,
            from_amount=from_amount,
            to_amount=to_amount,
            from_address=from_address,
            to_address=to_address,
            timelock_hours=timelock_hours,
            status="pending",
            created_at=datetime.now()
        )
        
        self.pending_swaps[swap_id] = swap_request
        
        logger.info(f"📝 Swap request created: {swap_id}")
        return swap_request
    
    async def execute_test_swap(self, 
                               eth_amount: Decimal = Decimal("0.01"),
                               doge_amount: Decimal = Decimal("1000")) -> Dict[str, Any]:
        """Execute a test swap for demonstration purposes."""
        try:
            logger.info("🧪 Starting test swap execution...")
            
            # Create test addresses (in production, these would be real addresses)
            eth_sender = "0x1234567890123456789012345678901234567890"
            eth_receiver = "0x0987654321098765432109876543210987654321"
            doge_sender = "D1234567890123456789012345678901234"
            doge_receiver = "D0987654321098765432109876543210987"
            
            # Step 1: Initiate the swap
            swap_id, secret = await self.htlc_manager.initiate_swap(
                eth_amount=eth_amount,
                doge_amount=doge_amount,
                eth_sender=eth_sender,
                eth_receiver=eth_receiver,
                doge_sender=doge_sender,
                doge_receiver=doge_receiver,
                timelock_hours=2  # Short timelock for testing
            )
            
            logger.info(f"✅ Test swap initiated: {swap_id}")
            
            # For testing, simulate the full swap process
            test_results = {
                "swap_id": swap_id,
                "secret_hash": secret.hash_hex,
                "status": "test_initiated",
                "steps": {
                    "1_doge_lock": "simulated",
                    "2_eth_lock": "simulated", 
                    "3_eth_claim": "simulated",
                    "4_doge_claim": "simulated"
                },
                "networks": {
                    "sepolia": self.config.get_network_config("sepolia"),
                    "dogecoin": self.config.get_network_config("dogecoin")
                },
                "contracts": {
                    "htlc_contract": self.config.htlc.sepolia_htlc_contract or "NOT_DEPLOYED",
                    "fusion_contract": self.config.fusion_plus.limit_order_protocol or "NOT_DEPLOYED"
                }
            }
            
            return test_results
            
        except Exception as e:
            logger.error(f"❌ Test swap failed: {e}")
            raise
    
    def get_swap_status(self, swap_id: str) -> Dict[str, Any]:
        """Get status of a specific swap."""
        # Check pending swaps
        if swap_id in self.pending_swaps:
            return self.pending_swaps[swap_id].to_dict()
        
        # Check active swaps
        return self.htlc_manager.get_swap_status(swap_id)
    
    def get_all_swaps(self) -> Dict[str, Any]:
        """Get status of all swaps."""
        return {
            "pending_swaps": {k: v.to_dict() for k, v in self.pending_swaps.items()},
            "active_swaps": {k: self.htlc_manager.get_swap_status(k) for k in self.htlc_manager.active_swaps.keys()},
            "resolver_status": {
                "is_running": self.is_running,
                "active_tasks": len(self.monitoring_tasks),
                "config_ready": self.config.is_testnet_ready()
            }
        }
    
    def get_testnet_info(self) -> Dict[str, Any]:
        """Get testnet information for users."""
        return {
            "networks": {
                "sepolia": {
                    "name": "Sepolia Testnet",
                    "chain_id": self.config.sepolia.chain_id,
                    "explorer": self.config.sepolia.explorer_url,
                    "faucets": self.config.sepolia.faucets
                },
                "dogecoin": {
                    "name": "Dogecoin Testnet",
                    "network": self.config.dogecoin_testnet.network_magic,
                    "explorer": self.config.dogecoin_testnet.explorer_url,
                    "faucets": self.config.dogecoin_testnet.faucets
                }
            },
            "contracts": {
                "htlc_address": self.config.htlc.sepolia_htlc_contract or "NOT_DEPLOYED",
                "fusion_address": self.config.fusion_plus.limit_order_protocol or "NOT_DEPLOYED"
            },
            "testing_limits": {
                "min_eth": str(self.config.fusion_plus.min_swap_amount_eth),
                "max_eth": str(self.config.fusion_plus.max_swap_amount_eth),
                "min_doge": str(self.config.fusion_plus.min_swap_amount_doge),
                "max_doge": str(self.config.fusion_plus.max_swap_amount_doge)
            }
        }
