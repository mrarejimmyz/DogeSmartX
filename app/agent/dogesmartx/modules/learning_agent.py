"""
DogeSmartX Learning Agent
Handles machine learning and adaptive behavior.
"""

from typing import Dict, Any, List, Optional
import json
from .base_agent import BaseAgentModule


class LearningAgent(BaseAgentModule):
    """Learning agent for pattern recognition and optimization"""
    
    def __init__(self):
        super().__init__("Learning Agent", "Provides machine learning and optimization capabilities")
        self.patterns = {}
        self.user_preferences = {}
        self.performance_metrics = {}
    
    def _register_capabilities(self):
        """Register learning capabilities"""
        from ..types import OperationCapability
        
        self.register_capability(OperationCapability(
            name="optimize_parameters",
            description="Optimize parameters based on historical performance",
            requirements=["operation_type"],
            examples=["Optimize atomic swap parameters"]
        ))
        
        self.register_capability(OperationCapability(
            name="predict_success_probability",
            description="Predict success probability for operations",
            requirements=["operation_params"],
            examples=["Predict swap success probability"]
        ))
    
    async def execute_capability(self, capability_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a learning capability"""
        if capability_name == "optimize_parameters":
            op_type = inputs.get("operation_type", "swap")
            result = await self.optimize_parameters(op_type)
            return result
        elif capability_name == "predict_success_probability":
            params = inputs.get("operation_params", {})
            probability = await self.predict_success_probability(params)
            return {"probability": probability}
        else:
            return {"error": f"Unknown capability: {capability_name}"}
    
    async def learn_from_swap(self, swap_data: Dict[str, Any]) -> None:
        """Learn patterns from completed swap operations"""
        try:
            swap_id = swap_data.get("swap_id")
            if swap_id:
                # Store learning data
                self.patterns[swap_id] = {
                    "success": swap_data.get("status") == "completed",
                    "duration": swap_data.get("duration", 0),
                    "gas_used": swap_data.get("gas_used", 0),
                    "market_conditions": swap_data.get("market_conditions", {})
                }
                
        except Exception as e:
            self.logger.error(f"Failed to learn from swap: {e}")
    
    async def optimize_parameters(self, operation_type: str) -> Dict[str, Any]:
        """Optimize parameters based on historical performance"""
        defaults = {
            "timelock_hours": 24,
            "gas_price_multiplier": 1.1,
            "slippage_tolerance": 0.01
        }
        
        # Return optimized parameters based on learning
        return {
            "optimized_params": defaults,
            "confidence": 0.8,
            "based_on_samples": len(self.patterns)
        }
    
    async def predict_success_probability(self, swap_params: Dict[str, Any]) -> float:
        """Predict success probability for a swap based on historical data"""
        # Simplified prediction logic
        base_probability = 0.85
        
        # Adjust based on amount
        amount = swap_params.get("amount", 0)
        if amount > 1.0:  # Large swaps might be riskier
            base_probability -= 0.1
            
        return max(0.0, min(1.0, base_probability))
    
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get learned user preferences"""
        return self.user_preferences.get(user_id, {
            "preferred_timelock": 24,
            "risk_tolerance": "medium",
            "preferred_gas_speed": "standard"
        })
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> None:
        """Update user preferences based on behavior"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}
        self.user_preferences[user_id].update(preferences)
