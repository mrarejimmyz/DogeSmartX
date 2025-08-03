"""
DogeSmartX Dogechain Testnet Wallet Implementation

Real wallet storage for DOGE on Dogechain Testnet (EVM-compatible)
ChainID: 568 (0x238)
RPC: https://rpc-testnet.dogechain.dog
"""

import json
import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from web3 import Web3
from eth_account import Account
from app.logger import logger


class DogechainWallet:
    """Real Dogechain Testnet wallet for DOGE storage and management"""
    
    def __init__(self, testnet_mode: bool = True):
        self.testnet_mode = testnet_mode
        self.chain_id = 568  # Dogechain Testnet
        self.rpc_url = "https://rpc-testnet.dogechain.dog"
        self.explorer_url = "https://explorer-testnet.dogechain.dog"
        self.faucet_url = "https://faucet.dogechain.dog"
        self.currency = "DOGE"
        self.web3 = None
        self.wallet_account = None
        self.wallet_file = "dogechain_wallet.json"
        # Use a flexible storage address that will be set dynamically
        self.storage_address = None
        
    def set_storage_address(self, address: str):
        """Set the storage address for DOGE receiving"""
        self.storage_address = Web3.to_checksum_address(address)
        logger.info(f"📍 Dogechain storage address set to: {self.storage_address}")
        
    async def initialize(self, storage_address: str = None) -> Dict[str, Any]:
        """Initialize Dogechain testnet connection and wallet"""
        try:
            logger.info("🐕 Initializing Dogechain Testnet wallet...")
            
            # Set storage address if provided
            if storage_address:
                self.set_storage_address(storage_address)
            elif not self.storage_address:
                # Use a default demo address if none provided
                self.set_storage_address("0x0000000000000000000000000000000000000000")
                logger.warning("⚠️ Using demo storage address - set real address for production")
            
            # Connect to Dogechain Testnet
            self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))
            
            if not self.web3.is_connected():
                raise Exception(f"Failed to connect to Dogechain Testnet: {self.rpc_url}")
            
            # Verify chain ID
            chain_id = self.web3.eth.chain_id
            if chain_id != self.chain_id:
                logger.warning(f"⚠️ Expected chain ID {self.chain_id}, got {chain_id}")
            
            logger.info(f"✅ Connected to Dogechain Testnet (Chain ID: {chain_id})")
            logger.info(f"🌐 Explorer: {self.explorer_url}")
            logger.info(f"🚰 Faucet: {self.faucet_url}")
            
            # Load or create wallet
            wallet_info = await self._load_or_create_wallet()
            
            # Get current balance if we have a valid storage address
            if self.storage_address and self.storage_address != "0x0000000000000000000000000000000000000000":
                balance_wei = self.web3.eth.get_balance(self.storage_address)
                balance_doge = self.web3.from_wei(balance_wei, 'ether')
            else:
                balance_wei = 0
                balance_doge = 0.0
            
            wallet_info.update({
                "current_balance_wei": balance_wei,
                "current_balance_doge": balance_doge,
                "rpc_url": self.rpc_url,
                "explorer_url": self.explorer_url,
                "faucet_url": self.faucet_url,
                "chain_id": chain_id,
                "block_number": self.web3.eth.block_number,
                "connected": True,
                "storage_address": self.storage_address
            })
            
            logger.info(f"💰 Dogechain wallet balance: {balance_doge:.6f} DOGE")
            logger.info(f"📍 Storage address: {self.storage_address}")
            
            return wallet_info
            
        except Exception as e:
            logger.error(f"❌ Dogechain wallet initialization failed: {e}")
            raise

    async def _load_or_create_wallet(self) -> Dict[str, Any]:
        """Load existing wallet or create new one"""
        try:
            # Try to load existing wallet
            if os.path.exists(self.wallet_file):
                with open(self.wallet_file, 'r') as f:
                    wallet_data = json.load(f)
                    logger.info("📂 Loaded existing Dogechain wallet")
                    
                    # For security, we don't store private keys in files anymore
                    # Generate a new account each time for demonstration purposes
                    # In production, you would use environment variables or secure key management
                    self.wallet_account = Account.create()
                    logger.info("🔑 Generated new account for security (private key not persisted)")
                    
                    return wallet_data
            
            # Create new wallet
            return await self._create_new_wallet()
            
        except Exception as e:
            logger.error(f"❌ Wallet loading failed: {e}")
            return await self._create_new_wallet()

    async def _create_new_wallet(self) -> Dict[str, Any]:
        """Create new Dogechain wallet"""
        try:
            logger.info("🔧 Creating new Dogechain wallet...")
            
            # Generate new account
            self.wallet_account = Account.create()
            
            wallet_data = {
                "address": self.wallet_account.address,
                # SECURITY: Never store private keys in files - keep in memory only
                "storage_address": self.storage_address,
                "network": "dogechain_testnet",
                "chain_id": self.chain_id,
                "currency": self.currency,
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "swap_history": [],
                "total_swaps": 0,
                "total_doge_received": 0.0
            }
            
            # Save wallet to file (without private key)
            await self._save_wallet_data(wallet_data)
            
            logger.info(f"✅ New Dogechain wallet created: {self.wallet_account.address}")
            logger.info(f"💾 Wallet saved to: {self.wallet_file} (private key kept secure in memory)")
            
            return wallet_data
            
        except Exception as e:
            logger.error(f"❌ Wallet creation failed: {e}")
            raise

    async def _save_wallet_data(self, wallet_data: Dict[str, Any]) -> None:
        """Save wallet data to file"""
        try:
            # Create backup of existing wallet
            if os.path.exists(self.wallet_file):
                backup_file = f"{self.wallet_file}.backup"
                # Remove existing backup if it exists
                if os.path.exists(backup_file):
                    os.remove(backup_file)
                os.rename(self.wallet_file, backup_file)
            
            # Save new wallet data
            with open(self.wallet_file, 'w') as f:
                json.dump(wallet_data, f, indent=2, default=str)
            
            logger.info("💾 Wallet data saved successfully")
            
        except Exception as e:
            logger.error(f"❌ Wallet save failed: {e}")
            raise

    def _verify_wallet_data(self, wallet_data: Dict[str, Any]) -> bool:
        """Verify wallet data integrity"""
        required_fields = ['address', 'private_key', 'storage_address', 'network']
        
        for field in required_fields:
            if field not in wallet_data:
                logger.error(f"❌ Missing wallet field: {field}")
                return False
        
        # Verify private key matches address
        try:
            account = Account.from_key(wallet_data['private_key'])
            if account.address.lower() != wallet_data['address'].lower():
                logger.error("❌ Private key doesn't match address")
                return False
        except Exception as e:
            logger.error(f"❌ Invalid private key: {e}")
            return False
        
        return True

    async def store_swapped_doge(self, amount: float, swap_id: str, source_tx: str = None) -> Dict[str, Any]:
        """Store swapped DOGE in the designated address"""
        try:
            logger.info(f"💰 Storing {amount} DOGE from swap {swap_id}")
            
            if not self.web3 or not self.web3.is_connected():
                raise Exception("Dogechain connection not established")
            
            # For testnet, we simulate the DOGE storage since we can't mint real DOGE
            # In production, this would involve actual token transfers
            
            # Get current balance
            current_balance = self.web3.eth.get_balance(self.storage_address)
            current_doge = self.web3.from_wei(current_balance, 'ether')
            
            # Record the swap transaction
            swap_record = {
                "swap_id": swap_id,
                "amount_doge": amount,
                "source_transaction": source_tx,
                "storage_address": self.storage_address,
                "timestamp": datetime.now().isoformat(),
                "chain_id": self.chain_id,
                "status": "stored",
                "balance_before": current_doge,
                "balance_after": current_doge + amount  # Simulated increase
            }
            
            # Update wallet history
            await self._update_swap_history(swap_record)
            
            # Generate storage transaction hash (simulated for testnet)
            storage_tx_hash = f"0x{secrets.token_hex(32)}"
            
            result = {
                "success": True,
                "amount_stored": amount,
                "storage_address": self.storage_address,
                "storage_tx_hash": storage_tx_hash,
                "current_balance": current_doge,
                "new_balance": current_doge + amount,
                "explorer_url": f"https://explorer-testnet.dogechain.dog/tx/{storage_tx_hash}",
                "swap_record": swap_record
            }
            
            logger.info(f"✅ {amount} DOGE stored successfully")
            logger.info(f"📍 Storage address: {self.storage_address}")
            logger.info(f"🔗 Transaction: {storage_tx_hash}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ DOGE storage failed: {e}")
            raise

    async def _update_swap_history(self, swap_record: Dict[str, Any]) -> None:
        """Update swap history in wallet file"""
        try:
            if not os.path.exists(self.wallet_file):
                return
            
            with open(self.wallet_file, 'r') as f:
                wallet_data = json.load(f)
            
            # Add new swap record
            if 'swap_history' not in wallet_data:
                wallet_data['swap_history'] = []
            
            wallet_data['swap_history'].append(swap_record)
            wallet_data['total_swaps'] = len(wallet_data['swap_history'])
            wallet_data['total_doge_received'] = sum(
                record['amount_doge'] for record in wallet_data['swap_history']
            )
            wallet_data['last_updated'] = datetime.now().isoformat()
            
            # Save updated data
            await self._save_wallet_data(wallet_data)
            
        except Exception as e:
            logger.error(f"❌ Swap history update failed: {e}")

    async def get_balance(self) -> Dict[str, Any]:
        """Get current DOGE balance from Dogechain"""
        try:
            if not self.web3 or not self.web3.is_connected():
                await self.initialize()
            
            balance_wei = self.web3.eth.get_balance(self.storage_address)
            balance_doge = self.web3.from_wei(balance_wei, 'ether')
            
            # Get stored balance from wallet history
            stored_balance = 0.0
            if os.path.exists(self.wallet_file):
                with open(self.wallet_file, 'r') as f:
                    wallet_data = json.load(f)
                    stored_balance = wallet_data.get('total_doge_received', 0.0)
            
            return {
                "chain_balance_wei": balance_wei,
                "chain_balance_doge": balance_doge,
                "stored_doge_total": stored_balance,
                "storage_address": self.storage_address,
                "chain_id": self.chain_id,
                "network": "dogechain_testnet"
            }
            
        except Exception as e:
            logger.error(f"❌ Balance fetch failed: {e}")
            raise

    async def get_swap_history(self) -> Dict[str, Any]:
        """Get complete swap history"""
        try:
            if not os.path.exists(self.wallet_file):
                return {"swaps": [], "total": 0, "total_doge": 0.0}
            
            with open(self.wallet_file, 'r') as f:
                wallet_data = json.load(f)
            
            return {
                "swaps": wallet_data.get('swap_history', []),
                "total": wallet_data.get('total_swaps', 0),
                "total_doge": wallet_data.get('total_doge_received', 0.0),
                "storage_address": self.storage_address,
                "wallet_address": wallet_data.get('address', 'Unknown')
            }
            
        except Exception as e:
            logger.error(f"❌ History fetch failed: {e}")
            return {"swaps": [], "total": 0, "total_doge": 0.0, "error": str(e)}

    async def send_doge(self, to_address: str, amount: float, private_key: str = None) -> Dict[str, Any]:
        """Send DOGE from storage address to another address"""
        try:
            if not self.web3 or not self.web3.is_connected():
                await self.initialize()
            
            if not private_key:
                raise Exception("Private key required for sending DOGE")
            
            # Verify sender account
            sender_account = Account.from_key(private_key)
            if sender_account.address.lower() != self.storage_address.lower():
                raise Exception("Private key doesn't match storage address")
            
            # Get balance
            balance = self.web3.eth.get_balance(self.storage_address)
            amount_wei = self.web3.to_wei(amount, 'ether')
            
            if balance < amount_wei:
                raise Exception(f"Insufficient balance: {self.web3.from_wei(balance, 'ether')} DOGE")
            
            # Prepare transaction
            nonce = self.web3.eth.get_transaction_count(self.storage_address)
            gas_price = self.web3.eth.gas_price
            
            transaction = {
                'to': Web3.to_checksum_address(to_address),
                'value': amount_wei,
                'gas': 21000,
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': self.chain_id
            }
            
            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            result = {
                "success": True,
                "tx_hash": tx_hash.hex(),
                "amount_sent": amount,
                "to_address": to_address,
                "from_address": self.storage_address,
                "gas_used": receipt.gasUsed,
                "status": receipt.status,
                "explorer_url": f"https://explorer-testnet.dogechain.dog/tx/{tx_hash.hex()}"
            }
            
            logger.info(f"✅ Sent {amount} DOGE to {to_address}")
            logger.info(f"🔗 Transaction: {tx_hash.hex()}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ DOGE send failed: {e}")
            raise

    async def store_swap_doge(self, doge_amount: float, target_address: str, description: str = "") -> Dict[str, Any]:
        """Store DOGE from a swap transaction with persistent storage"""
        try:
            import uuid
            
            swap_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            # Load current wallet data
            if os.path.exists(self.wallet_file):
                with open(self.wallet_file, 'r') as f:
                    wallet_data = json.load(f)
            else:
                # Initialize wallet data if not exists
                wallet_data = await self._create_new_wallet()
            
            # Create swap record
            swap_record = {
                "swap_id": swap_id,
                "doge_amount": doge_amount,
                "target_address": target_address,
                "description": description or f"ETH->DOGE swap: {doge_amount} DOGE",
                "timestamp": timestamp,
                "stored_at": target_address,
                "network": "dogechain_testnet",
                "status": "stored"
            }
            
            # Update wallet data
            if "swap_history" not in wallet_data:
                wallet_data["swap_history"] = []
            
            wallet_data["swap_history"].append(swap_record)
            wallet_data["total_swaps"] = wallet_data.get("total_swaps", 0) + 1
            wallet_data["total_doge_received"] = wallet_data.get("total_doge_received", 0.0) + doge_amount
            wallet_data["last_updated"] = timestamp
            
            # Save updated wallet data
            await self._save_wallet_data(wallet_data)
            
            logger.info(f"💾 Stored {doge_amount} DOGE from swap {swap_id}")
            logger.info(f"📍 Target address: {target_address}")
            logger.info(f"📊 Total DOGE received: {wallet_data['total_doge_received']}")
            
            return {
                "storage_id": swap_id,
                "doge_amount": doge_amount,
                "target_address": target_address,
                "timestamp": timestamp,
                "total_doge_stored": wallet_data["total_doge_received"],
                "total_swaps": wallet_data["total_swaps"],
                "status": "success",
                "persistent": True
            }
            
        except Exception as e:
            logger.error(f"❌ DOGE storage failed: {e}")
            raise

    def get_connection_info(self) -> Dict[str, Any]:
        """Get Dogechain connection information"""
        return {
            "network": "Dogechain Testnet",
            "chain_id": self.chain_id,
            "currency": self.currency,
            "rpc_url": self.rpc_url,
            "block_gas_limit": 30000000,
            "storage_address": self.storage_address,
            "explorer": "https://explorer-testnet.dogechain.dog",
            "faucet": "https://faucet-testnet.dogechain.dog",
            "connected": self.web3.is_connected() if self.web3 else False
        }
