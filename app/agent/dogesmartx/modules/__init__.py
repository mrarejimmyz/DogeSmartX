"""
DogeSmartX Modular Agent System
Core modules for the revolutionary AI orchestration engine
"""

from .base_agent import BaseAgentModule
from .market_agent import MarketAnalysisAgent
from .sentiment_agent import SentimentAgent
from .wallet_agent import WalletAgent
from .execution_agent import ExecutionAgent
from .learning_agent import LearningAgent

__all__ = [
    'BaseAgentModule',
    'MarketAnalysisAgent', 
    'SentimentAgent',
    'WalletAgent',
    'ExecutionAgent',
    'LearningAgent'
]
