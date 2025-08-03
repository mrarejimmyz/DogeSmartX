# DogeSmartX Agent - Modular Architecture

## Overview

DogeSmartX is a modular, scalable, and easily debuggable AI-powered DeFi agent specializing in cross-chain swaps between Ethereum and Dogecoin. The agent combines cutting-edge blockchain technology with the playful spirit of the Dogecoin community.

## Architecture

### 🏗️ Modular Design

The DogeSmartX agent is built with a modular architecture for maximum scalability and maintainability:

```
dogesmartx/
├── __init__.py          # Module entry point
├── agent.py             # Main agent class
├── config.py            # Configuration management
├── exceptions.py        # Custom exception handling
├── models.py            # Pydantic data models
├── services.py          # Core business logic services
└── utils.py             # Helper functions and utilities
```

## Core Features

### 🔄 Bidirectional Cross-Chain Swaps
- **ETH ↔ DOGE** exchanges with full bidirectional support
- **1inch Fusion+** protocol integration for optimal routing
- **Real-time** route optimization and slippage protection
- **MEV resistance** and front-running protection

### 🔒 Atomic Swap Security
- **SHA256 hashlock** mechanisms for cryptographic security
- **Configurable timelock** protection (default 24 hours)
- **Non-custodial** and trustless transaction model
- **Multi-signature** support for large transactions

### ⛓️ Onchain Execution
- **Testnet deployment** ready for demonstrations
- **Limit Order Protocol** contract integration
- **Real transaction execution** with proper gas estimation
- **Cross-chain bridge** functionality for seamless swaps

### 💰 Partial Fills
- **Fractional order fulfillment** for better liquidity
- **Real-time progress tracking** with visual indicators
- **Better liquidity utilization** through order splitting
- **Continuous trading** capabilities while orders remain active

### 📊 Market Intelligence
- **Live price tracking** for DOGE and ETH
- **Gas fee optimization** with multi-tier recommendations
- **Optimal timing analysis** based on market conditions
- **Community sentiment** integration and tracking

### 🎭 Community Features
- **Meme-themed interface** elements and interactions
- **Social sentiment** integration from multiple sources
- **Dogecoin culture** preservation and celebration
- **Community-driven** recommendations and features

### 💝 Charity Integration
- **Automatic donation** deduction (0.1% of swap fees by default)
- **Transparent pool tracking** with public accountability
- **"Do Only Good Everyday"** philosophy implementation
- **Community cause** support and voting mechanisms

## Configuration

### Environment Variables

```bash
# Network Configuration
ETH_RPC_URL=https://sepolia.infura.io/v3/YOUR_KEY
DOGE_RPC_URL=http://localhost:18332

# Contract Addresses
LIMIT_ORDER_PROTOCOL_ADDRESS=0x...
DOGE_BRIDGE_ADDRESS=0x...
CHARITY_POOL_ADDRESS=0x...

# API Keys
INFURA_API_KEY=your_infura_key
COINGECKO_API_KEY=your_coingecko_key
ONEINCH_API_KEY=your_1inch_key

# Feature Flags
DOGESMARTX_DEBUG=true
PARTIAL_FILLS=true
CHARITY_ENABLED=true
MEME_MODE=true

# Trading Parameters
CHARITY_FEE=0.1
MIN_SWAP=0.001
MAX_SWAP=1000.0
TIMELOCK_HOURS=24
```

### Configuration Management

The agent uses a hierarchical configuration system:

1. **Default values** in `config.py`
2. **Environment variables** override defaults
3. **Runtime configuration** can be updated via API

## Data Models

### Type-Safe Models with Pydantic

```python
# Swap Order Model
class SwapOrder(BaseModel):
    swap_id: str
    direction: SwapDirection
    amount: Decimal
    status: SwapStatus
    secret_hash: str
    timelock_expiry: int
    partial_fills_enabled: bool
    # ... additional fields

# Market Data Model
class MarketData(BaseModel):
    symbol: str
    price_usd: Decimal
    timestamp: float
    source: Optional[str]
    # ... additional fields
```

## Service Architecture

### Core Services

1. **SwapService**: Manages cross-chain swap operations
2. **MarketService**: Handles market data and analysis
3. **ContractService**: Manages smart contract interactions
4. **CommunityService**: Handles community features and sentiment

### Service Integration

```python
# Service initialization
self.swap_service = SwapService(self.config, self.state)
self.market_service = MarketService(self.config, self.state)
self.contract_service = ContractService(self.config)
self.community_service = CommunityService(self.config, self.state)
```

## Error Handling

### Comprehensive Exception System

```python
# Custom exceptions with context
class SwapError(DogeSmartXError):
    def __init__(self, message: str, swap_id: Optional[str] = None, 
                 direction: Optional[str] = None, amount: Optional[float] = None):
        context = {"swap_id": swap_id, "direction": direction, "amount": amount}
        super().__init__(message, "SWAP_ERROR", context)

# Exception handling decorator
@handle_exception
async def create_swap(self, direction, amount):
    # Function implementation
    pass
```

### Error Categories

- **SwapError**: Swap operation failures
- **ContractError**: Smart contract interaction issues
- **NetworkError**: Blockchain network problems
- **ValidationError**: Input validation failures
- **MarketDataError**: Market data retrieval issues
- **TimeoutError**: Operation timeout failures

## Debugging and Monitoring

### Debug Mode Features

- **Comprehensive logging** with structured context
- **State inspection** tools for real-time monitoring
- **Performance metrics** tracking and analysis
- **Error tracking** with full stack traces
- **Configuration validation** with detailed reports

### Debug Commands

```python
# System status check
"debug status"

# Service health monitoring
"debug services"

# Configuration inspection
"debug config"

# Active swap analysis
"debug swaps"
```

## Usage Examples

### Basic Swap Operations

```python
# Create a bidirectional swap
"swap 1 ETH to DOGE"
"swap 100 DOGE to ETH"

# Enable partial fills
"swap 0.5 ETH to DOGE with partial fills"

# Execute partial fill
"fill 0.1 for abcd1234efgh5678"
```

### Market Analysis

```python
# Get market data
"market analysis"

# Check gas fees
"gas fees ethereum"

# Swap recommendations
"optimal timing analysis"
```

### Onchain Operations

```python
# Check deployment status
"deploy to testnet"

# Contract verification
"check contracts"

# Network status
"onchain status"
```

### Community Features

```python
# Community sentiment
"community sentiment"

# Charity pool status
"charity pool"

# Meme interface
"enable meme mode"
```

## Development

### Adding New Features

1. **Define models** in `models.py` with proper typing
2. **Implement service logic** in appropriate service class
3. **Add error handling** with custom exceptions
4. **Create tests** for new functionality
5. **Update documentation** and examples

### Testing

```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=dogesmartx tests/

# Debug mode testing
DOGESMARTX_DEBUG=true python -m pytest tests/
```

### Contributing

1. Follow the modular architecture patterns
2. Use proper type hints and Pydantic models
3. Implement comprehensive error handling
4. Add debug logging for important operations
5. Maintain the Dogecoin community spirit! 🐕

## Deployment

### Production Deployment

1. **Configure environment** variables
2. **Deploy smart contracts** to target networks
3. **Verify contract** addresses in configuration
4. **Enable monitoring** and logging
5. **Test with small amounts** before full deployment

### Security Considerations

- **Never expose private keys** in configuration
- **Use environment variables** for sensitive data
- **Validate all inputs** before processing
- **Implement rate limiting** for API calls
- **Monitor for suspicious activity**

## Community

### Dogecoin Spirit

DogeSmartX maintains the fun, inclusive, and community-driven spirit of Dogecoin:

- **"Do Only Good Everyday"** philosophy
- **Meme integration** and playful interactions
- **Community governance** for major decisions
- **Charity contributions** from every transaction
- **Accessible technology** for everyone

### Contributing

We welcome contributions that:
- Improve security and functionality
- Enhance user experience
- Add community features
- Support charitable causes
- Maintain the fun factor! 🚀

---

**Much technology, such architecture, very scalable!** 🐕🌕

Ready to revolutionize DeFi with Dogecoin spirit! 🚀💎
