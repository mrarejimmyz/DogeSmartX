"""
DogeSmartX AI Agent Orchestration Engine
=======================================

Revolutionary multi-agent coordination system that leverages existing LLM infrastructure
to provide autonomous DeFi trading experience.

🧠 Core Philosophy:
- Use existing centralized LLM for intent recognition and decision making
- Coordinate multiple specialized agents simultaneously  
- Provide conversational interface for complex DeFi operations
- Autonomous execution with human-like reasoning

🎯 Agent Types:
- Market Analysis Agent: Real-time price and trend analysis
- Sentiment Agent: Social media and news sentiment tracking  
- Wallet Agent: Transaction execution and wallet management
- Browser Agent: Web automation and research
- Learning Agent: Pattern recognition and strategy optimization

✨ Revolutionary Features:
- Natural language to complex DeFi operations
- Multi-agent decision making
- Autonomous portfolio management
- Real-time problem solving
- Continuous learning and adaptation
"""

from .master_orchestrator import MasterAIOrchestrator
from .intent_processor import IntentProcessor
from .agent_coordinator import AgentCoordinator
from .execution_engine import ExecutionEngine

__all__ = [
    "MasterAIOrchestrator",
    "IntentProcessor", 
    "AgentCoordinator",
    "ExecutionEngine"
]
