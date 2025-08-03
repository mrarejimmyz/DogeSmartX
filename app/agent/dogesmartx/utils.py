"""
DogeSmartX Utilities Module

Helper functions and utilities for DogeSmartX agent operations.
"""

import hashlib
import secrets
import time
import re
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal


def generate_swap_id(direction: str, amount: Decimal, extra_data: str = "") -> str:
    """Generate a unique swap ID using SHA256 hash."""
    timestamp = str(time.time())
    data = f"{direction}{amount}{timestamp}{extra_data}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def generate_secret_pair() -> Tuple[str, str]:
    """Generate a secret and its SHA256 hash for atomic swaps."""
    secret = secrets.token_hex(32)
    secret_hash = hashlib.sha256(secret.encode()).hexdigest()
    return secret, secret_hash


def parse_amount_from_text(text: str, default: float = 1.0) -> Decimal:
    """Extract numeric amount from text using regex."""
    amount_match = re.search(r'(\d+(?:\.\d+)?)', text)
    amount = float(amount_match.group(1)) if amount_match else default
    return Decimal(str(amount))


def parse_swap_direction(text: str) -> Optional[str]:
    """Parse swap direction from text."""
    text_lower = text.lower()
    
    if any(phrase in text_lower for phrase in ["eth to doge", "ethereum to dogecoin"]):
        return "eth_to_doge"
    elif any(phrase in text_lower for phrase in ["doge to eth", "dogecoin to ethereum"]):
        return "doge_to_eth"
    
    return None


def format_currency(amount: Decimal, symbol: str = "$", decimals: int = 4) -> str:
    """Format currency amount with proper decimals."""
    return f"{symbol}{amount:.{decimals}f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format percentage with proper decimals."""
    return f"{value:.{decimals}f}%"


def calculate_time_remaining(expiry_timestamp: int) -> Dict[str, Any]:
    """Calculate time remaining until expiry."""
    current_time = int(time.time())
    time_remaining = expiry_timestamp - current_time
    
    if time_remaining <= 0:
        return {
            "expired": True,
            "hours": 0,
            "minutes": 0,
            "seconds": 0,
            "total_seconds": 0
        }
    
    hours = time_remaining // 3600
    minutes = (time_remaining % 3600) // 60
    seconds = time_remaining % 60
    
    return {
        "expired": False,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
        "total_seconds": time_remaining
    }


def validate_ethereum_address(address: str) -> bool:
    """Validate Ethereum address format."""
    if not address:
        return False
    
    # Remove 0x prefix if present
    if address.startswith("0x"):
        address = address[2:]
    
    # Check length and hex format
    if len(address) != 40:
        return False
    
    try:
        int(address, 16)
        return True
    except ValueError:
        return False


def calculate_slippage(expected_amount: Decimal, actual_amount: Decimal) -> Decimal:
    """Calculate slippage percentage."""
    if expected_amount == 0:
        return Decimal("0")
    
    slippage = abs(expected_amount - actual_amount) / expected_amount * 100
    return slippage


def format_gas_estimate(gas_amount: int, gas_price_gwei: float) -> Dict[str, str]:
    """Format gas estimate with cost calculation."""
    gas_cost_eth = (gas_amount * gas_price_gwei) / 1e9
    
    return {
        "gas_limit": f"{gas_amount:,}",
        "gas_price": f"{gas_price_gwei} gwei",
        "estimated_cost": f"{gas_cost_eth:.6f} ETH",
        "estimated_cost_usd": "TBD"  # Would require ETH price
    }


def create_transaction_summary(
    swap_id: str,
    direction: str,
    amount: Decimal,
    status: str,
    timestamps: Dict[str, float]
) -> Dict[str, Any]:
    """Create a comprehensive transaction summary."""
    duration = None
    if "created_at" in timestamps and "completed_at" in timestamps:
        duration = timestamps["completed_at"] - timestamps["created_at"]
    
    return {
        "swap_id": swap_id,
        "direction": direction.replace("_", " → ").upper(),
        "amount": str(amount),
        "status": status.replace("_", " ").title(),
        "duration_seconds": duration,
        "created_at": timestamps.get("created_at"),
        "completed_at": timestamps.get("completed_at"),
        "updated_at": timestamps.get("updated_at")
    }


def generate_meme_response(success: bool = True) -> str:
    """Generate a Dogecoin-themed response."""
    if success:
        responses = [
            "Much success! 🐕🚀",
            "Such transaction! Very secure! 💎",
            "Wow! Much atomic swap! 🌕",
            "To the moon! 🚀🌕",
            "Very DeFi! Much wow! ✨",
            "Such technology! 🔧✨"
        ]
    else:
        responses = [
            "Much oops! Try again! 🐕",
            "Such error! Very fixable! 🔧",
            "Wow! Need more debugging! 🐛",
            "Much retry needed! 🔄",
            "Such challenge! Very growth! 📈"
        ]
    
    import random
    return random.choice(responses)


def sanitize_user_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input for security."""
    # Remove potential harmful characters
    sanitized = re.sub(r'[<>"\']', '', text)
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()


def format_debug_info(
    component: str,
    status: str,
    details: Dict[str, Any],
    timestamp: Optional[float] = None
) -> str:
    """Format debug information consistently."""
    timestamp_str = ""
    if timestamp:
        import datetime
        dt = datetime.datetime.fromtimestamp(timestamp)
        timestamp_str = f" [{dt.strftime('%Y-%m-%d %H:%M:%S')}]"
    
    details_str = "\n".join(f"  {k}: {v}" for k, v in details.items())
    
    return f"""🐛 DEBUG: {component}{timestamp_str}
Status: {status}
Details:
{details_str}
"""


def extract_swap_id_from_text(text: str) -> Optional[str]:
    """Extract swap ID (16-char hex) from text."""
    match = re.search(r'\b([a-f0-9]{16})\b', text.lower())
    return match.group(1) if match else None


def calculate_charity_contribution(
    amount: Decimal,
    fee_percentage: float,
    min_contribution: Decimal = Decimal("0.0001")
) -> Decimal:
    """Calculate charity contribution with minimum threshold."""
    contribution = amount * Decimal(str(fee_percentage / 100))
    return max(contribution, min_contribution)


def format_network_status(
    network_name: str,
    is_connected: bool,
    block_height: Optional[int] = None,
    gas_price: Optional[float] = None
) -> str:
    """Format network status information."""
    status_icon = "✅" if is_connected else "❌"
    status_text = "Connected" if is_connected else "Disconnected"
    
    info = f"{status_icon} {network_name}: {status_text}"
    
    if block_height:
        info += f" (Block: {block_height:,})"
    
    if gas_price:
        info += f" (Gas: {gas_price} gwei)"
    
    return info


def validate_swap_parameters(
    direction: str,
    amount: Decimal,
    min_amount: Decimal,
    max_amount: Decimal
) -> List[str]:
    """Validate swap parameters and return list of errors."""
    errors = []
    
    if direction not in ["eth_to_doge", "doge_to_eth"]:
        errors.append(f"Invalid direction: {direction}")
    
    if amount <= 0:
        errors.append("Amount must be positive")
    
    if amount < min_amount:
        errors.append(f"Amount below minimum: {min_amount}")
    
    if amount > max_amount:
        errors.append(f"Amount exceeds maximum: {max_amount}")
    
    return errors


def create_progress_bar(
    current: float,
    total: float,
    width: int = 20,
    fill_char: str = "█",
    empty_char: str = "░"
) -> str:
    """Create a visual progress bar."""
    if total == 0:
        percentage = 0
    else:
        percentage = min(current / total, 1.0)
    
    filled_width = int(width * percentage)
    empty_width = width - filled_width
    
    bar = fill_char * filled_width + empty_char * empty_width
    percentage_text = f"{percentage * 100:.1f}%"
    
    return f"{bar} {percentage_text}"
