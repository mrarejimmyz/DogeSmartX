"""
CoinGecko API Simulator for DogeSmartX
Provides realistic market data simulation with price variations
"""

import json
import time
import random
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from decimal import Decimal, ROUND_HALF_UP
import math

class CoinGeckoSimulator:
    """
    Realistic CoinGecko API simulator with dynamic price variations
    Simulates real market behavior with volatility and trends
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.coingecko.com/api/v3"
        self.request_count = 0
        self.last_request_time = time.time()
        
        # Base prices (as of simulation start)
        self.base_prices = {
            "dogecoin": 0.08234,  # DOGE price in USD
            "ethereum": 2456.78,  # ETH price in USD
            "bitcoin": 43250.55   # BTC price in USD
        }
        
        # Price trends (for realistic variations)
        self.price_trends = {
            "dogecoin": {"trend": "bullish", "volatility": 0.05, "momentum": 0.02},
            "ethereum": {"trend": "neutral", "volatility": 0.03, "momentum": 0.01},
            "bitcoin": {"trend": "bearish", "volatility": 0.025, "momentum": -0.015}
        }
        
        # Market data cache (simulates real-time updates)
        self.market_cache = {}
        self.cache_expiry = 30  # 30 seconds cache
        
        # Initialize simulation start time
        self.simulation_start = time.time()
    
    async def get_price(self, ids: str, vs_currencies: str = "usd", 
                       include_market_cap: bool = True, 
                       include_24hr_vol: bool = True,
                       include_24hr_change: bool = True) -> Dict[str, Any]:
        """
        Simulate /simple/price endpoint with realistic variations
        """
        await self._simulate_rate_limit()
        
        coin_ids = ids.split(",")
        currencies = vs_currencies.split(",")
        
        response = {}
        
        for coin_id in coin_ids:
            if coin_id not in self.base_prices:
                continue
                
            coin_data = {}
            current_price = self._get_dynamic_price(coin_id)
            
            for currency in currencies:
                # Simulate currency conversion (simplified)
                if currency == "usd":
                    price = current_price
                elif currency == "eur":
                    price = current_price * 0.92  # EUR conversion
                elif currency == "btc":
                    price = current_price / self._get_dynamic_price("bitcoin")
                else:
                    price = current_price
                
                coin_data[currency] = round(price, 8)
                
                if include_market_cap:
                    market_cap = self._calculate_market_cap(coin_id, price)
                    coin_data[f"{currency}_market_cap"] = market_cap
                
                if include_24hr_vol:
                    volume_24h = self._calculate_24h_volume(coin_id, price)
                    coin_data[f"{currency}_24h_vol"] = volume_24h
                
                if include_24hr_change:
                    change_24h = self._calculate_24h_change(coin_id)
                    coin_data[f"{currency}_24h_change"] = change_24h
            
            response[coin_id] = coin_data
        
        self._log_api_call("simple/price", {"ids": ids, "vs_currencies": vs_currencies})
        return response
    
    async def get_coins_markets(self, vs_currency: str = "usd", 
                               ids: Optional[str] = None,
                               order: str = "market_cap_desc",
                               per_page: int = 100,
                               page: int = 1) -> List[Dict[str, Any]]:
        """
        Simulate /coins/markets endpoint with comprehensive market data
        """
        await self._simulate_rate_limit()
        
        coins_to_include = ids.split(",") if ids else list(self.base_prices.keys())
        markets_data = []
        
        for coin_id in coins_to_include:
            if coin_id not in self.base_prices:
                continue
            
            current_price = self._get_dynamic_price(coin_id)
            market_cap = self._calculate_market_cap(coin_id, current_price)
            
            coin_market_data = {
                "id": coin_id,
                "symbol": self._get_symbol(coin_id),
                "name": self._get_name(coin_id),
                "image": f"https://assets.coingecko.com/coins/images/{coin_id}.png",
                "current_price": round(current_price, 8),
                "market_cap": market_cap,
                "market_cap_rank": self._get_market_cap_rank(coin_id),
                "fully_diluted_valuation": market_cap * 1.1,
                "total_volume": self._calculate_24h_volume(coin_id, current_price),
                "high_24h": round(current_price * (1 + random.uniform(0.05, 0.15)), 8),
                "low_24h": round(current_price * (1 - random.uniform(0.05, 0.15)), 8),
                "price_change_24h": self._calculate_price_change_24h(coin_id, current_price),
                "price_change_percentage_24h": self._calculate_24h_change(coin_id),
                "market_cap_change_24h": self._calculate_market_cap_change_24h(coin_id),
                "market_cap_change_percentage_24h": random.uniform(-8.5, 12.3),
                "circulating_supply": self._get_circulating_supply(coin_id),
                "total_supply": self._get_total_supply(coin_id),
                "max_supply": self._get_max_supply(coin_id),
                "ath": self._get_ath(coin_id),
                "ath_change_percentage": self._calculate_ath_change(coin_id, current_price),
                "ath_date": self._get_ath_date(coin_id),
                "atl": self._get_atl(coin_id),
                "atl_change_percentage": self._calculate_atl_change(coin_id, current_price),
                "atl_date": self._get_atl_date(coin_id),
                "roi": self._calculate_roi(coin_id),
                "last_updated": datetime.utcnow().isoformat() + "Z"
            }
            
            markets_data.append(coin_market_data)
        
        # Sort by market cap descending (default)
        if order == "market_cap_desc":
            markets_data.sort(key=lambda x: x["market_cap"], reverse=True)
        
        self._log_api_call("coins/markets", {"vs_currency": vs_currency, "ids": ids})
        return markets_data
    
    async def get_coin_history(self, coin_id: str, date: str, 
                              localization: bool = False) -> Dict[str, Any]:
        """
        Simulate /coins/{id}/history endpoint for historical data
        """
        await self._simulate_rate_limit()
        
        if coin_id not in self.base_prices:
            raise ValueError(f"Coin {coin_id} not found")
        
        # Parse date and calculate historical price
        try:
            target_date = datetime.strptime(date, "%d-%m-%Y")
            days_ago = (datetime.now() - target_date).days
            
            # Simulate price evolution backwards
            base_price = self.base_prices[coin_id]
            historical_multiplier = 1 + (random.uniform(-0.3, 0.3) * (days_ago / 365))
            historical_price = base_price * historical_multiplier
            
            response = {
                "id": coin_id,
                "symbol": self._get_symbol(coin_id),
                "name": self._get_name(coin_id),
                "localization": {} if not localization else {"en": self._get_name(coin_id)},
                "image": {
                    "thumb": f"https://assets.coingecko.com/coins/images/{coin_id}_thumb.png",
                    "small": f"https://assets.coingecko.com/coins/images/{coin_id}_small.png",
                    "large": f"https://assets.coingecko.com/coins/images/{coin_id}_large.png"
                },
                "market_data": {
                    "current_price": {
                        "usd": round(historical_price, 8),
                        "eur": round(historical_price * 0.92, 8),
                        "btc": round(historical_price / self.base_prices["bitcoin"], 10)
                    },
                    "market_cap": {
                        "usd": self._calculate_market_cap(coin_id, historical_price),
                        "eur": self._calculate_market_cap(coin_id, historical_price * 0.92)
                    },
                    "total_volume": {
                        "usd": self._calculate_24h_volume(coin_id, historical_price),
                        "eur": self._calculate_24h_volume(coin_id, historical_price * 0.92)
                    }
                },
                "community_data": {
                    "facebook_likes": random.randint(10000, 100000),
                    "twitter_followers": random.randint(50000, 500000),
                    "reddit_average_posts_48h": random.uniform(5, 50),
                    "reddit_average_comments_48h": random.uniform(20, 200)
                },
                "public_interest_stats": {
                    "alexa_rank": random.randint(1000, 10000),
                    "bing_matches": random.randint(100000, 1000000)
                }
            }
            
            self._log_api_call(f"coins/{coin_id}/history", {"date": date})
            return response
            
        except ValueError as e:
            raise ValueError(f"Invalid date format: {date}. Use DD-MM-YYYY")
    
    def _get_dynamic_price(self, coin_id: str) -> float:
        """
        Calculate dynamic price with realistic variations
        """
        if coin_id not in self.base_prices:
            return 0.0
        
        base_price = self.base_prices[coin_id]
        trend_data = self.price_trends[coin_id]
        
        # Time-based variations
        time_elapsed = time.time() - self.simulation_start
        hours_elapsed = time_elapsed / 3600
        
        # Trend influence (long-term)
        trend_multiplier = 1 + (trend_data["momentum"] * hours_elapsed / 24)
        
        # Volatility (short-term random walk)
        volatility = trend_data["volatility"]
        random_variation = random.uniform(-volatility, volatility)
        
        # Market cycle influence (sine wave for natural-looking cycles)
        cycle_influence = math.sin(time_elapsed / 1800) * volatility * 0.5  # 30-min cycles
        
        # News/event spikes (rare random events)
        news_spike = 0
        if random.random() < 0.001:  # 0.1% chance per call
            news_spike = random.uniform(-0.15, 0.25)  # -15% to +25% spike
        
        total_multiplier = trend_multiplier * (1 + random_variation + cycle_influence + news_spike)
        
        # Ensure price doesn't go negative or extreme
        total_multiplier = max(0.1, min(10.0, total_multiplier))
        
        current_price = base_price * total_multiplier
        
        # Update trend momentum based on price movement
        if current_price > base_price * 1.05:
            self.price_trends[coin_id]["momentum"] += 0.001
        elif current_price < base_price * 0.95:
            self.price_trends[coin_id]["momentum"] -= 0.001
        
        return current_price
    
    def _calculate_market_cap(self, coin_id: str, price: float) -> int:
        """Calculate realistic market cap"""
        supply = self._get_circulating_supply(coin_id)
        return int(price * supply)
    
    def _calculate_24h_volume(self, coin_id: str, price: float) -> int:
        """Calculate realistic 24h trading volume"""
        base_volumes = {
            "dogecoin": 800000000,    # $800M
            "ethereum": 15000000000,  # $15B
            "bitcoin": 25000000000    # $25B
        }
        
        base_volume = base_volumes.get(coin_id, 100000000)
        volatility_multiplier = 1 + random.uniform(-0.3, 0.5)
        
        return int(base_volume * volatility_multiplier)
    
    def _calculate_24h_change(self, coin_id: str) -> float:
        """Calculate realistic 24h price change percentage"""
        volatility = self.price_trends[coin_id]["volatility"]
        momentum = self.price_trends[coin_id]["momentum"]
        
        base_change = momentum * 24  # Convert hourly momentum to daily
        random_change = random.uniform(-volatility * 100, volatility * 100)
        
        total_change = base_change * 100 + random_change
        return round(total_change, 2)
    
    def _calculate_price_change_24h(self, coin_id: str, current_price: float) -> float:
        """Calculate absolute price change in 24h"""
        percentage_change = self._calculate_24h_change(coin_id)
        return round((current_price * percentage_change / 100), 8)
    
    def _calculate_market_cap_change_24h(self, coin_id: str) -> int:
        """Calculate market cap change in 24h"""
        current_market_cap = self._calculate_market_cap(coin_id, self._get_dynamic_price(coin_id))
        change_percentage = self._calculate_24h_change(coin_id)
        return int(current_market_cap * change_percentage / 100)
    
    async def _simulate_rate_limit(self):
        """Simulate API rate limiting"""
        self.request_count += 1
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self.last_request_time > 60:
            self.request_count = 1
            self.last_request_time = current_time
        
        # Simulate rate limit (50 calls per minute for free tier)
        if self.request_count > 50:
            await asyncio.sleep(1)  # Simulate rate limit delay
    
    def _log_api_call(self, endpoint: str, params: Dict[str, Any]):
        """Log API calls for debugging"""
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] CoinGecko API Call: {endpoint} - {params}")
    
    # Helper methods for coin data
    def _get_symbol(self, coin_id: str) -> str:
        symbols = {"dogecoin": "doge", "ethereum": "eth", "bitcoin": "btc"}
        return symbols.get(coin_id, coin_id[:4].upper())
    
    def _get_name(self, coin_id: str) -> str:
        names = {"dogecoin": "Dogecoin", "ethereum": "Ethereum", "bitcoin": "Bitcoin"}
        return names.get(coin_id, coin_id.title())
    
    def _get_market_cap_rank(self, coin_id: str) -> int:
        ranks = {"bitcoin": 1, "ethereum": 2, "dogecoin": 8}
        return ranks.get(coin_id, 100)
    
    def _get_circulating_supply(self, coin_id: str) -> float:
        supplies = {
            "dogecoin": 142000000000,    # 142B DOGE
            "ethereum": 120000000,       # 120M ETH
            "bitcoin": 19700000          # 19.7M BTC
        }
        return supplies.get(coin_id, 1000000)
    
    def _get_total_supply(self, coin_id: str) -> Optional[float]:
        supplies = {
            "dogecoin": 142000000000,
            "ethereum": 120000000,
            "bitcoin": 19700000
        }
        return supplies.get(coin_id)
    
    def _get_max_supply(self, coin_id: str) -> Optional[float]:
        max_supplies = {
            "dogecoin": None,  # No max supply
            "ethereum": None,  # No max supply
            "bitcoin": 21000000  # 21M BTC max
        }
        return max_supplies.get(coin_id)
    
    def _get_ath(self, coin_id: str) -> float:
        aths = {
            "dogecoin": 0.7376,    # May 2021
            "ethereum": 4891.70,   # Nov 2021
            "bitcoin": 69045       # Nov 2021
        }
        return aths.get(coin_id, self.base_prices.get(coin_id, 1.0))
    
    def _get_ath_date(self, coin_id: str) -> str:
        ath_dates = {
            "dogecoin": "2021-05-08T05:08:23.458Z",
            "ethereum": "2021-11-10T14:24:19.604Z",
            "bitcoin": "2021-11-10T14:24:11.849Z"
        }
        return ath_dates.get(coin_id, "2021-11-10T00:00:00.000Z")
    
    def _get_atl(self, coin_id: str) -> float:
        atls = {
            "dogecoin": 0.00008547,  # May 2015
            "ethereum": 0.432979,    # Oct 2015
            "bitcoin": 67.81         # Jul 2013
        }
        return atls.get(coin_id, self.base_prices.get(coin_id, 1.0) * 0.1)
    
    def _get_atl_date(self, coin_id: str) -> str:
        atl_dates = {
            "dogecoin": "2015-05-06T09:02:28.301Z",
            "ethereum": "2015-10-20T09:55:58.548Z",
            "bitcoin": "2013-07-06T00:00:00.000Z"
        }
        return atl_dates.get(coin_id, "2015-01-01T00:00:00.000Z")
    
    def _calculate_ath_change(self, coin_id: str, current_price: float) -> float:
        ath = self._get_ath(coin_id)
        return round(((current_price - ath) / ath) * 100, 2)
    
    def _calculate_atl_change(self, coin_id: str, current_price: float) -> float:
        atl = self._get_atl(coin_id)
        return round(((current_price - atl) / atl) * 100, 2)
    
    def _calculate_roi(self, coin_id: str) -> Optional[Dict[str, float]]:
        """Calculate return on investment (simplified)"""
        if coin_id == "ethereum":  # ETH had ICO
            return {
                "times": 245.67,
                "currency": "usd",
                "percentage": 24567.0
            }
        return None


# Integration with DogeSmartX
class DogeSmartXMarketData:
    """
    Market data service for DogeSmartX using CoinGecko simulator
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.coingecko = CoinGeckoSimulator(api_key)
        self.cache = {}
        self.cache_ttl = 30  # 30 seconds
    
    async def get_doge_eth_prices(self) -> Dict[str, float]:
        """Get current DOGE and ETH prices for swap calculations"""
        cache_key = "doge_eth_prices"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        
        try:
            prices = await self.coingecko.get_price(
                ids="dogecoin,ethereum",
                vs_currencies="usd",
                include_24hr_change=True
            )
            
            result = {
                "doge_usd": prices["dogecoin"]["usd"],
                "eth_usd": prices["ethereum"]["usd"],
                "doge_eth_ratio": prices["dogecoin"]["usd"] / prices["ethereum"]["usd"],
                "doge_change_24h": prices["dogecoin"]["usd_24h_change"],
                "eth_change_24h": prices["ethereum"]["usd_24h_change"]
            }
            
            self._cache_data(cache_key, result)
            return result
            
        except Exception as e:
            print(f"Error fetching prices: {e}")
            # Return fallback data
            return {
                "doge_usd": 0.08234,
                "eth_usd": 2456.78,
                "doge_eth_ratio": 0.08234 / 2456.78,
                "doge_change_24h": 0.0,
                "eth_change_24h": 0.0
            }
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """Get comprehensive market overview for DogeSmartX dashboard"""
        cache_key = "market_overview"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        
        try:
            markets = await self.coingecko.get_coins_markets(
                ids="dogecoin,ethereum,bitcoin",
                vs_currency="usd"
            )
            
            result = {
                "coins": {coin["id"]: coin for coin in markets},
                "total_market_cap": sum(coin["market_cap"] for coin in markets),
                "total_volume_24h": sum(coin["total_volume"] for coin in markets),
                "last_updated": datetime.utcnow().isoformat() + "Z"
            }
            
            self._cache_data(cache_key, result)
            return result
            
        except Exception as e:
            print(f"Error fetching market overview: {e}")
            return {"error": str(e)}
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache:
            return False
        
        cache_time = self.cache[key]["timestamp"]
        return (time.time() - cache_time) < self.cache_ttl
    
    def _cache_data(self, key: str, data: Any):
        """Cache data with timestamp"""
        self.cache[key] = {
            "data": data,
            "timestamp": time.time()
        }


# Example usage and testing
async def test_coingecko_simulator():
    """Test the CoinGecko simulator with realistic scenarios"""
    print("🧪 Testing CoinGecko API Simulator")
    print("=" * 50)
    
    # Initialize simulator
    cg = CoinGeckoSimulator(api_key="demo_key_123")
    market_data = DogeSmartXMarketData()
    
    # Test 1: Basic price fetching
    print("📊 Test 1: Basic Price Fetching")
    prices = await cg.get_price("dogecoin,ethereum", "usd", True, True, True)
    print(json.dumps(prices, indent=2))
    
    # Test 2: Market data
    print("\n📈 Test 2: Market Data")
    markets = await cg.get_coins_markets(ids="dogecoin,ethereum")
    print(json.dumps(markets[0], indent=2))
    
    # Test 3: DogeSmartX market integration
    print("\n🚀 Test 3: DogeSmartX Market Integration")
    doge_eth_prices = await market_data.get_doge_eth_prices()
    print(json.dumps(doge_eth_prices, indent=2))
    
    # Test 4: Multiple calls to show price variations
    print("\n📊 Test 4: Price Variations Over Time")
    for i in range(3):
        await asyncio.sleep(2)  # Wait 2 seconds between calls
        varied_prices = await cg.get_price("dogecoin", "usd")
        print(f"Call {i+1}: DOGE = ${varied_prices['dogecoin']['usd']:.6f}")
    
    print("\n✅ CoinGecko Simulator Testing Complete!")

if __name__ == "__main__":
    asyncio.run(test_coingecko_simulator())
