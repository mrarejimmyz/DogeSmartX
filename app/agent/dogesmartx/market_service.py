"""
DogeSmartX Market Service
Integrates CoinGecko simulator with DogeSmartX agent for real-time market data
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from .coingecko_simulator import CoinGeckoSimulator, DogeSmartXMarketData
from .advanced_config import DogeSmartXAdvancedConfig

logger = logging.getLogger(__name__)

class MarketService:
    """
    Central market data service for DogeSmartX
    Provides price feeds, market analysis, and swap optimization data
    """
    
    def __init__(self, config: DogeSmartXAdvancedConfig):
        self.config = config
        self.api_key = config.api_keys.get("coingecko", "")
        
        # Initialize simulators
        self.coingecko = CoinGeckoSimulator(self.api_key)
        self.market_data = DogeSmartXMarketData(self.api_key)
        
        # Market analysis state
        self.current_prices = {}
        self.price_history = []
        self.market_trends = {}
        self.last_update = None
        
        logger.info("🔄 DogeSmartX Market Service initialized")
    
    async def initialize(self) -> None:
        """Initialize market service with initial data fetch"""
        try:
            await self.update_market_data()
            logger.info("✅ Market Service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Market Service initialization failed: {e}")
            # Continue with default values
            self.current_prices = {
                "doge_usd": 0.08234,
                "eth_usd": 2456.78,
                "doge_eth_ratio": 0.08234 / 2456.78
            }
    
    async def update_market_data(self) -> None:
        """Update all market data from CoinGecko simulator"""
        try:
            # Fetch current prices
            prices = await self.market_data.get_doge_eth_prices()
            self.current_prices.update(prices)
            
            # Store price history for trend analysis
            self.price_history.append({
                "timestamp": datetime.now(),
                "doge_usd": prices["doge_usd"],
                "eth_usd": prices["eth_usd"],
                "doge_eth_ratio": prices["doge_eth_ratio"]
            })
            
            # Keep only last 100 price points
            if len(self.price_history) > 100:
                self.price_history.pop(0)
            
            # Update market trends
            await self._analyze_trends()
            
            self.last_update = datetime.now()
            logger.info(f"📈 Market data updated: DOGE=${prices['doge_usd']:.6f}, ETH=${prices['eth_usd']:.2f}")
            
        except Exception as e:
            logger.error(f"❌ Error updating market data: {e}")
    
    async def get_swap_quote(self, from_token: str, to_token: str, amount: float) -> Dict[str, Any]:
        """
        Get swap quote with current market prices and slippage calculations
        """
        try:
            await self.update_market_data()
            
            # Calculate swap amounts based on current prices
            if from_token.lower() == "doge" and to_token.lower() == "eth":
                rate = self.current_prices["doge_eth_ratio"]
                output_amount = amount * rate
                price_impact = self._calculate_price_impact(amount, "doge")
                
            elif from_token.lower() == "eth" and to_token.lower() == "doge":
                rate = 1 / self.current_prices["doge_eth_ratio"]
                output_amount = amount * rate
                price_impact = self._calculate_price_impact(amount, "eth")
                
            else:
                raise ValueError(f"Unsupported token pair: {from_token}/{to_token}")
            
            # Calculate fees and slippage
            network_fee = self._calculate_network_fee(from_token)
            slippage = self.config.trading_config.max_slippage
            min_output = output_amount * (1 - slippage)
            
            quote = {
                "from_token": from_token.upper(),
                "to_token": to_token.upper(),
                "input_amount": amount,
                "output_amount": output_amount,
                "min_output_amount": min_output,
                "exchange_rate": rate,
                "price_impact": price_impact,
                "network_fee": network_fee,
                "slippage_tolerance": slippage * 100,  # Convert to percentage
                "valid_until": (datetime.now() + timedelta(minutes=5)).isoformat(),
                "market_prices": {
                    "doge_usd": self.current_prices["doge_usd"],
                    "eth_usd": self.current_prices["eth_usd"]
                },
                "confidence": self._calculate_quote_confidence()
            }
            
            logger.info(f"💱 Swap quote: {amount} {from_token} → {output_amount:.6f} {to_token}")
            return quote
            
        except Exception as e:
            logger.error(f"❌ Error calculating swap quote: {e}")
            raise
    
    async def get_optimal_swap_timing(self) -> Dict[str, Any]:
        """
        Analyze market conditions to recommend optimal swap timing
        """
        try:
            if len(self.price_history) < 10:
                return {
                    "recommendation": "neutral",
                    "confidence": 0.5,
                    "reason": "Insufficient historical data for analysis"
                }
            
            # Analyze recent price trends
            recent_prices = self.price_history[-10:]
            price_trend = self._calculate_price_trend(recent_prices)
            volatility = self._calculate_volatility(recent_prices)
            momentum = self._calculate_momentum(recent_prices)
            
            # Generate recommendation
            if price_trend > 0.02 and momentum > 0.01:
                recommendation = "wait"
                reason = "Upward trend detected, prices may continue rising"
                confidence = min(0.8, abs(price_trend) * 10)
                
            elif price_trend < -0.02 and momentum < -0.01:
                recommendation = "buy_dip"
                reason = "Downward trend detected, potential buying opportunity"
                confidence = min(0.8, abs(price_trend) * 10)
                
            elif volatility > 0.05:
                recommendation = "wait_for_stability"
                reason = "High volatility detected, wait for market stabilization"
                confidence = min(0.9, volatility * 10)
                
            else:
                recommendation = "neutral"
                reason = "Market conditions are stable, good time for regular swaps"
                confidence = 0.7
            
            return {
                "recommendation": recommendation,
                "confidence": confidence,
                "reason": reason,
                "market_metrics": {
                    "price_trend": price_trend,
                    "volatility": volatility,
                    "momentum": momentum
                },
                "current_prices": self.current_prices,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing swap timing: {e}")
            return {
                "recommendation": "neutral",
                "confidence": 0.5,
                "reason": f"Analysis error: {str(e)}"
            }
    
    async def get_market_sentiment(self) -> Dict[str, Any]:
        """
        Get market sentiment analysis based on price movements and trends
        """
        try:
            # Fetch comprehensive market data
            market_overview = await self.market_data.get_market_overview()
            
            if "error" in market_overview:
                return {"sentiment": "neutral", "confidence": 0.5}
            
            coins_data = market_overview.get("coins", {})
            
            # Analyze sentiment based on 24h changes
            sentiment_scores = []
            for coin_id, coin_data in coins_data.items():
                change_24h = coin_data.get("price_change_percentage_24h", 0)
                volume_ratio = coin_data.get("total_volume", 0) / max(coin_data.get("market_cap", 1), 1)
                
                # Calculate sentiment score
                if change_24h > 5:
                    score = 1  # Very bullish
                elif change_24h > 2:
                    score = 0.5  # Bullish
                elif change_24h > -2:
                    score = 0  # Neutral
                elif change_24h > -5:
                    score = -0.5  # Bearish
                else:
                    score = -1  # Very bearish
                
                # Weight by volume (higher volume = more reliable signal)
                weighted_score = score * min(volume_ratio * 100, 1)
                sentiment_scores.append(weighted_score)
            
            # Calculate overall sentiment
            if sentiment_scores:
                avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                
                if avg_sentiment > 0.3:
                    sentiment = "bullish"
                elif avg_sentiment < -0.3:
                    sentiment = "bearish"
                else:
                    sentiment = "neutral"
                
                confidence = min(0.9, abs(avg_sentiment) + 0.3)
            else:
                sentiment = "neutral"
                confidence = 0.5
            
            return {
                "sentiment": sentiment,
                "confidence": confidence,
                "sentiment_score": avg_sentiment if sentiment_scores else 0,
                "contributing_factors": {
                    "doge_change_24h": coins_data.get("dogecoin", {}).get("price_change_percentage_24h", 0),
                    "eth_change_24h": coins_data.get("ethereum", {}).get("price_change_percentage_24h", 0),
                    "btc_change_24h": coins_data.get("bitcoin", {}).get("price_change_percentage_24h", 0)
                },
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing market sentiment: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "error": str(e)
            }
    
    def _calculate_price_impact(self, amount: float, token: str) -> float:
        """Calculate price impact for large trades"""
        # Simplified price impact calculation
        if token.lower() == "doge":
            # DOGE has higher liquidity, lower impact
            base_impact = amount / 1000000  # 1M DOGE for 0.1% impact
        else:  # ETH
            # ETH has good liquidity
            base_impact = amount / 1000  # 1000 ETH for 0.1% impact
        
        return min(0.05, base_impact)  # Cap at 5% impact
    
    def _calculate_network_fee(self, token: str) -> float:
        """Calculate network fees for transactions"""
        if token.lower() == "doge":
            return 1.0  # 1 DOGE network fee
        else:  # ETH
            return 0.005  # 0.005 ETH network fee (~$12 at current prices)
    
    def _calculate_quote_confidence(self) -> float:
        """Calculate confidence level for swap quote"""
        if not self.price_history:
            return 0.5
        
        # Higher confidence with more data and lower volatility
        data_confidence = min(1.0, len(self.price_history) / 50)
        
        recent_volatility = self._calculate_volatility(self.price_history[-10:])
        volatility_confidence = max(0.3, 1.0 - recent_volatility * 10)
        
        return (data_confidence + volatility_confidence) / 2
    
    async def _analyze_trends(self) -> None:
        """Analyze price trends for market intelligence"""
        if len(self.price_history) < 5:
            return
        
        # Calculate various trend indicators
        recent_prices = self.price_history[-10:]
        
        self.market_trends = {
            "doge_trend": self._calculate_price_trend(recent_prices, "doge_usd"),
            "eth_trend": self._calculate_price_trend(recent_prices, "eth_usd"),
            "ratio_trend": self._calculate_price_trend(recent_prices, "doge_eth_ratio"),
            "volatility": self._calculate_volatility(recent_prices),
            "momentum": self._calculate_momentum(recent_prices)
        }
    
    def _calculate_price_trend(self, price_data: List[Dict], price_key: str = "doge_usd") -> float:
        """Calculate price trend (positive = upward, negative = downward)"""
        if len(price_data) < 2:
            return 0.0
        
        prices = [point[price_key] for point in price_data]
        
        # Simple linear trend calculation
        n = len(prices)
        x_sum = sum(range(n))
        y_sum = sum(prices)
        xy_sum = sum(i * prices[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))
        
        if n * x2_sum - x_sum * x_sum == 0:
            return 0.0
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        return slope / (y_sum / n)  # Normalize by average price
    
    def _calculate_volatility(self, price_data: List[Dict], price_key: str = "doge_usd") -> float:
        """Calculate price volatility (standard deviation)"""
        if len(price_data) < 2:
            return 0.0
        
        prices = [point[price_key] for point in price_data]
        avg_price = sum(prices) / len(prices)
        
        variance = sum((price - avg_price) ** 2 for price in prices) / len(prices)
        volatility = (variance ** 0.5) / avg_price  # Normalize by average price
        
        return volatility
    
    def _calculate_momentum(self, price_data: List[Dict], price_key: str = "doge_usd") -> float:
        """Calculate price momentum (rate of change acceleration)"""
        if len(price_data) < 3:
            return 0.0
        
        prices = [point[price_key] for point in price_data]
        
        # Calculate rate of change for each period
        rates = []
        for i in range(1, len(prices)):
            rate = (prices[i] - prices[i-1]) / prices[i-1]
            rates.append(rate)
        
        # Momentum is the acceleration of rate of change
        if len(rates) < 2:
            return 0.0
        
        momentum = rates[-1] - rates[-2]  # Latest change vs previous change
        return momentum


# Testing function
async def test_market_service():
    """Test the market service functionality"""
    from .advanced_config import DogeSmartXAdvancedConfig
    
    print("🧪 Testing DogeSmartX Market Service")
    print("=" * 50)
    
    # Initialize config and service
    config = DogeSmartXAdvancedConfig()
    market_service = MarketService(config)
    
    await market_service.initialize()
    
    # Test swap quote
    print("💱 Testing Swap Quote")
    quote = await market_service.get_swap_quote("DOGE", "ETH", 1000)
    print(f"Quote: {quote['input_amount']} {quote['from_token']} → {quote['output_amount']:.6f} {quote['to_token']}")
    print(f"Rate: 1 {quote['from_token']} = {quote['exchange_rate']:.8f} {quote['to_token']}")
    
    # Test optimal timing
    print("\n⏰ Testing Optimal Timing")
    timing = await market_service.get_optimal_swap_timing()
    print(f"Recommendation: {timing['recommendation']} (confidence: {timing['confidence']:.2f})")
    print(f"Reason: {timing['reason']}")
    
    # Test market sentiment
    print("\n📊 Testing Market Sentiment")
    sentiment = await market_service.get_market_sentiment()
    print(f"Sentiment: {sentiment['sentiment']} (confidence: {sentiment['confidence']:.2f})")
    
    print("\n✅ Market Service Testing Complete!")

if __name__ == "__main__":
    asyncio.run(test_market_service())
