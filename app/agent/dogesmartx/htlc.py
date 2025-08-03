"""
HTLC (Hash Time-Locked Contract) Implementation for Sepolia-Dogecoin Swaps

This module implements the Hash Time-Locked Contract logic for secure
cross-chain atomic swaps between Sepolia ETH and Dogecoin testnet.
"""

import hashlib
import secrets
import time
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

from app.logger import logger


@dataclass
class HTLCSecret:
    """HTLC secret and hash pair."""
    secret: bytes
    hash: bytes
    hash_hex: str
    
    @classmethod
    def generate(cls) -> 'HTLCSecret':
        """Generate a new HTLC secret."""
        secret = secrets.token_bytes(32)  # 32-byte secret
        hash_bytes = hashlib.sha256(secret).digest()
        hash_hex = hash_bytes.hex()
        
        return cls(
            secret=secret,
            hash=hash_bytes,
            hash_hex=hash_hex
        )
    
    @classmethod
    def from_secret(cls, secret: bytes) -> 'HTLCSecret':
        """Create HTLC secret from existing secret."""
        hash_bytes = hashlib.sha256(secret).digest()
        hash_hex = hash_bytes.hex()
        
        return cls(
            secret=secret,
            hash=hash_bytes,
            hash_hex=hash_hex
        )


@dataclass
class HTLCParameters:
    """Parameters for HTLC creation."""
    sender: str
    receiver: str
    amount: Decimal
    hash_lock: str  # Hex string of hash
    time_lock: int  # Unix timestamp
    network: str
    
    def is_expired(self) -> bool:
        """Check if HTLC has expired."""
        return int(time.time()) >= self.time_lock
    
    def time_remaining(self) -> int:
        """Get remaining time in seconds."""
        return max(0, self.time_lock - int(time.time()))


@dataclass
class HTLCContract:
    """Represents an HTLC contract."""
    contract_id: str
    parameters: HTLCParameters
    status: str  # 'pending', 'claimed', 'refunded', 'expired'
    creation_block: Optional[int] = None
    creation_tx: Optional[str] = None
    claim_tx: Optional[str] = None
    refund_tx: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "contract_id": self.contract_id,
            "sender": self.parameters.sender,
            "receiver": self.parameters.receiver,
            "amount": str(self.parameters.amount),
            "hash_lock": self.parameters.hash_lock,
            "time_lock": self.parameters.time_lock,
            "network": self.parameters.network,
            "status": self.status,
            "creation_block": self.creation_block,
            "creation_tx": self.creation_tx,
            "claim_tx": self.claim_tx,
            "refund_tx": self.refund_tx
        }


class SepoliaHTLCService:
    """HTLC service for Sepolia ETH operations."""
    
    def __init__(self, web3_provider, contract_address: str, contract_abi: Dict):
        self.w3 = web3_provider
        self.contract_address = contract_address
        self.contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)
        logger.info(f"🔐 Sepolia HTLC Service initialized at {contract_address}")
    
    async def create_htlc(self, parameters: HTLCParameters, private_key: str) -> HTLCContract:
        """Create HTLC on Sepolia."""
        try:
            # Build transaction
            account = self.w3.eth.account.from_key(private_key)
            nonce = self.w3.eth.get_transaction_count(account.address)
            
            # Convert parameters for contract call
            amount_wei = self.w3.to_wei(parameters.amount, 'ether')
            hash_bytes = bytes.fromhex(parameters.hash_lock)
            
            # Build contract transaction
            transaction = self.contract.functions.createHTLC(
                parameters.receiver,
                hash_bytes,
                parameters.time_lock
            ).build_transaction({
                'from': account.address,
                'value': amount_wei,
                'gas': 300000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
                'nonce': nonce
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Generate contract ID from transaction
            contract_id = f"sepolia_{receipt.transactionHash.hex()}"
            
            htlc = HTLCContract(
                contract_id=contract_id,
                parameters=parameters,
                status='pending',
                creation_block=receipt.blockNumber,
                creation_tx=receipt.transactionHash.hex()
            )
            
            logger.info(f"✅ Sepolia HTLC created: {contract_id}")
            return htlc
            
        except Exception as e:
            logger.error(f"❌ Failed to create Sepolia HTLC: {e}")
            raise
    
    async def claim_htlc(self, contract_id: str, secret: bytes, private_key: str) -> str:
        """Claim HTLC on Sepolia with secret."""
        try:
            account = self.w3.eth.account.from_key(private_key)
            nonce = self.w3.eth.get_transaction_count(account.address)
            
            # Extract contract parameters from blockchain
            # This would need the actual contract implementation
            
            transaction = self.contract.functions.claimHTLC(
                contract_id,
                secret
            ).build_transaction({
                'from': account.address,
                'gas': 200000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
                'nonce': nonce
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info(f"✅ Sepolia HTLC claimed: {contract_id}")
            return receipt.transactionHash.hex()
            
        except Exception as e:
            logger.error(f"❌ Failed to claim Sepolia HTLC: {e}")
            raise
    
    async def refund_htlc(self, contract_id: str, private_key: str) -> str:
        """Refund expired HTLC on Sepolia."""
        try:
            account = self.w3.eth.account.from_key(private_key)
            nonce = self.w3.eth.get_transaction_count(account.address)
            
            transaction = self.contract.functions.refundHTLC(
                contract_id
            ).build_transaction({
                'from': account.address,
                'gas': 150000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
                'nonce': nonce
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info(f"✅ Sepolia HTLC refunded: {contract_id}")
            return receipt.transactionHash.hex()
            
        except Exception as e:
            logger.error(f"❌ Failed to refund Sepolia HTLC: {e}")
            raise


class DogecoinHTLCService:
    """HTLC service for Dogecoin testnet operations."""
    
    def __init__(self, rpc_client):
        self.rpc = rpc_client
        logger.info("🐕 Dogecoin HTLC Service initialized")
    
    def create_htlc_script(self, parameters: HTLCParameters) -> str:
        """Create Dogecoin HTLC script."""
        # This is a simplified version - actual implementation would need
        # proper Dogecoin script construction
        
        script_template = f"""
        OP_IF
            OP_SHA256 
            {parameters.hash_lock} 
            OP_EQUALVERIFY 
            OP_DUP 
            OP_HASH160 
            {self._address_to_hash160(parameters.receiver)} 
        OP_ELSE 
            {parameters.time_lock} 
            OP_CHECKLOCKTIMEVERIFY 
            OP_DROP 
            OP_DUP 
            OP_HASH160 
            {self._address_to_hash160(parameters.sender)} 
        OP_ENDIF 
        OP_EQUALVERIFY 
        OP_CHECKSIG
        """
        
        return script_template.strip()
    
    def _address_to_hash160(self, address: str) -> str:
        """Convert Dogecoin address to hash160."""
        # Simplified implementation - would need proper base58 decoding
        return f"hash160_{address}"
    
    async def create_htlc(self, parameters: HTLCParameters, private_key: str) -> HTLCContract:
        """Create HTLC on Dogecoin testnet."""
        try:
            # Create HTLC script
            script = self.create_htlc_script(parameters)
            
            # Create transaction (simplified)
            # Actual implementation would use dogecoin libraries
            
            # For testing, we'll simulate the transaction
            contract_id = f"doge_{int(time.time())}_{secrets.token_hex(8)}"
            
            htlc = HTLCContract(
                contract_id=contract_id,
                parameters=parameters,
                status='pending',
                creation_tx=f"simulated_tx_{secrets.token_hex(32)}"
            )
            
            logger.info(f"✅ Dogecoin HTLC created: {contract_id}")
            return htlc
            
        except Exception as e:
            logger.error(f"❌ Failed to create Dogecoin HTLC: {e}")
            raise
    
    async def claim_htlc(self, contract_id: str, secret: bytes, private_key: str) -> str:
        """Claim HTLC on Dogecoin with secret."""
        try:
            # Create claim transaction with secret
            # Actual implementation would construct proper Dogecoin transaction
            
            tx_id = f"claim_tx_{secrets.token_hex(32)}"
            
            logger.info(f"✅ Dogecoin HTLC claimed: {contract_id}")
            return tx_id
            
        except Exception as e:
            logger.error(f"❌ Failed to claim Dogecoin HTLC: {e}")
            raise


class CrossChainHTLCManager:
    """Manager for cross-chain HTLC operations."""
    
    def __init__(self, sepolia_service: SepoliaHTLCService, dogecoin_service: DogecoinHTLCService):
        self.sepolia = sepolia_service
        self.dogecoin = dogecoin_service
        self.active_swaps: Dict[str, Dict[str, HTLCContract]] = {}
        logger.info("🌉 Cross-chain HTLC Manager initialized")
    
    async def initiate_swap(self, 
                          eth_amount: Decimal, 
                          doge_amount: Decimal,
                          eth_sender: str,
                          doge_receiver: str,
                          doge_sender: str,
                          eth_receiver: str,
                          timelock_hours: int = 24) -> Tuple[str, HTLCSecret]:
        """Initiate a cross-chain atomic swap."""
        try:
            # Generate HTLC secret
            htlc_secret = HTLCSecret.generate()
            
            # Calculate timelock
            timelock = int(time.time()) + (timelock_hours * 3600)
            
            # Create swap ID
            swap_id = f"swap_{int(time.time())}_{secrets.token_hex(8)}"
            
            # Create HTLC parameters for both chains
            eth_params = HTLCParameters(
                sender=eth_sender,
                receiver=eth_receiver,
                amount=eth_amount,
                hash_lock=htlc_secret.hash_hex,
                time_lock=timelock,
                network="sepolia"
            )
            
            doge_params = HTLCParameters(
                sender=doge_sender,
                receiver=doge_receiver,
                amount=doge_amount,
                hash_lock=htlc_secret.hash_hex,
                time_lock=timelock - 3600,  # DOGE expires 1 hour earlier for safety
                network="dogecoin_testnet"
            )
            
            # Store swap information
            self.active_swaps[swap_id] = {
                "eth_htlc": None,
                "doge_htlc": None,
                "secret": htlc_secret,
                "status": "initiated",
                "eth_params": eth_params,
                "doge_params": doge_params
            }
            
            logger.info(f"🚀 Cross-chain swap initiated: {swap_id}")
            return swap_id, htlc_secret
            
        except Exception as e:
            logger.error(f"❌ Failed to initiate swap: {e}")
            raise
    
    async def execute_swap_step1_doge_lock(self, swap_id: str, doge_private_key: str) -> str:
        """Step 1: Lock DOGE in HTLC."""
        try:
            swap_data = self.active_swaps[swap_id]
            doge_params = swap_data["doge_params"]
            
            # Create DOGE HTLC
            doge_htlc = await self.dogecoin.create_htlc(doge_params, doge_private_key)
            
            # Update swap data
            swap_data["doge_htlc"] = doge_htlc
            swap_data["status"] = "doge_locked"
            
            logger.info(f"✅ Step 1 complete - DOGE locked: {swap_id}")
            return doge_htlc.contract_id
            
        except Exception as e:
            logger.error(f"❌ Step 1 failed: {e}")
            raise
    
    async def execute_swap_step2_eth_lock(self, swap_id: str, eth_private_key: str) -> str:
        """Step 2: Lock ETH in HTLC (resolver action)."""
        try:
            swap_data = self.active_swaps[swap_id]
            eth_params = swap_data["eth_params"]
            
            # Create ETH HTLC
            eth_htlc = await self.sepolia.create_htlc(eth_params, eth_private_key)
            
            # Update swap data
            swap_data["eth_htlc"] = eth_htlc
            swap_data["status"] = "both_locked"
            
            logger.info(f"✅ Step 2 complete - ETH locked: {swap_id}")
            return eth_htlc.contract_id
            
        except Exception as e:
            logger.error(f"❌ Step 2 failed: {e}")
            raise
    
    async def execute_swap_step3_eth_claim(self, swap_id: str, eth_private_key: str) -> str:
        """Step 3: Claim ETH with secret."""
        try:
            swap_data = self.active_swaps[swap_id]
            secret = swap_data["secret"]
            eth_htlc = swap_data["eth_htlc"]
            
            # Claim ETH HTLC
            claim_tx = await self.sepolia.claim_htlc(
                eth_htlc.contract_id, 
                secret.secret, 
                eth_private_key
            )
            
            # Update swap data
            swap_data["status"] = "eth_claimed"
            eth_htlc.claim_tx = claim_tx
            eth_htlc.status = "claimed"
            
            logger.info(f"✅ Step 3 complete - ETH claimed: {swap_id}")
            return claim_tx
            
        except Exception as e:
            logger.error(f"❌ Step 3 failed: {e}")
            raise
    
    async def execute_swap_step4_doge_claim(self, swap_id: str, doge_private_key: str) -> str:
        """Step 4: Claim DOGE with revealed secret (resolver action)."""
        try:
            swap_data = self.active_swaps[swap_id]
            secret = swap_data["secret"]
            doge_htlc = swap_data["doge_htlc"]
            
            # Claim DOGE HTLC
            claim_tx = await self.dogecoin.claim_htlc(
                doge_htlc.contract_id,
                secret.secret,
                doge_private_key
            )
            
            # Update swap data
            swap_data["status"] = "completed"
            doge_htlc.claim_tx = claim_tx
            doge_htlc.status = "claimed"
            
            logger.info(f"✅ Step 4 complete - DOGE claimed: {swap_id}")
            logger.info(f"🎉 Cross-chain swap completed successfully: {swap_id}")
            
            return claim_tx
            
        except Exception as e:
            logger.error(f"❌ Step 4 failed: {e}")
            raise
    
    def get_swap_status(self, swap_id: str) -> Dict[str, Any]:
        """Get current status of a swap."""
        if swap_id not in self.active_swaps:
            return {"error": "Swap not found"}
        
        swap_data = self.active_swaps[swap_id]
        
        return {
            "swap_id": swap_id,
            "status": swap_data["status"],
            "eth_htlc": swap_data["eth_htlc"].to_dict() if swap_data["eth_htlc"] else None,
            "doge_htlc": swap_data["doge_htlc"].to_dict() if swap_data["doge_htlc"] else None,
            "secret_hash": swap_data["secret"].hash_hex
        }
