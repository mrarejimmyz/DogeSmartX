"""
DogeSmartX Operation Handlers

Core operation detection and routing logic for the DogeSmartX agent.
"""

import asyncio
from typing import Dict, Optional, Any
from app.logger import logger
from app.schema import Message
from .types import OperationResult, SwapRequest

# Import orchestration if available
try:
    from .orchestration_engine import process_conversational_request
    ORCHESTRATION_AVAILABLE = True
    logger.info("🎭 DogeSmartX Orchestration Engine available!")
except ImportError as e:
    logger.warning(f"Orchestration engine not available: {e}")
    ORCHESTRATION_AVAILABLE = False


class OperationDetector:
    """Detects and classifies DogeSmartX operations"""
    
    def __init__(self):
        self.conversational_indicators = [
            "when it's good", "automatically", "optimize", "manage my", 
            "something's wrong", "error", "failed", "help", "monitor",
            "analysis", "price", "market", "sentiment", "but not if",
            "rebalance", "portfolio", "how does", "explain", "learn"
        ]
        
        self.swap_indicators = [
            "atomic", "swap", "exchange", "trade", "execute", "real swap", "cross-chain"
        ]
        
        self.deployment_indicators = [
            "deploy", "contract", "htlc", "fusion"
        ]
        
        self.setup_indicators = [
            "wallet", "setup", "initialize", "connect"
        ]

    async def detect_operation_type(self, content: str) -> str:
        """Detect the type of DogeSmartX operation requested with AI orchestration."""
        content_lower = content.lower()
        
        # Check if this is a completion/success message that should terminate
        completion_indicators = [
            "real atomic swap execution completed",
            "atomic swap summary:",
            "technical implementation:",
            "dogesmartx is ready",
            "execution completed",
            "✅",
            "🎯 **real atomic swap summary:**"
        ]
        
        if any(indicator in content_lower for indicator in completion_indicators):
            logger.info("🏁 Detected completion message - triggering task complete")
            return "completion_message"
        
        # Check if this is a conversational DeFi request that needs orchestration
        if any(phrase in content_lower for phrase in self.conversational_indicators):
            if ORCHESTRATION_AVAILABLE:
                try:
                    logger.info("🎭 Routing to DogeSmartX Orchestration Engine for conversational DeFi")
                    
                    orchestration_result = await process_conversational_request(content)
                    
                    if orchestration_result.get("success"):
                        # Return special type that triggers orchestration flow
                        return "conversational_defi"
                    else:
                        logger.warning("Orchestration failed, falling back to standard detection")
                except Exception as e:
                    logger.warning(f"Orchestration engine not available: {e}, using standard detection")
        
        # Standard operation detection for simple requests
        if any(word in content_lower for word in self.swap_indicators):
            return "atomic_swap"
        elif any(word in content_lower for word in self.deployment_indicators):
            return "contract_deployment"
        elif any(word in content_lower for word in self.setup_indicators) and "swap" not in content_lower:
            return "wallet_setup"
        elif any(word in content_lower for word in ["resolver", "monitor", "automated"]):
            return "resolver_setup"
        elif any(word in content_lower for word in ["test"]) and "swap" not in content_lower:
            return "test_execution"
        else:
            return "atomic_swap"  # Default to atomic swap for DogeSmartX


class OperationRouter:
    """Routes operations to appropriate handlers"""
    
    def __init__(self, agent_instance):
        self.agent = agent_instance
        self.detector = OperationDetector()
        
        # Map operation types to handler methods
        self.operation_handlers = {
            "completion_message": "_handle_completion_message",
            "conversational_defi": "_execute_conversational_defi",
            "atomic_swap": "_execute_atomic_swap", 
            "contract_deployment": "_execute_contract_deployment",
            "wallet_setup": "_execute_wallet_setup",
            "resolver_setup": "_execute_resolver_setup",
            "test_execution": "_execute_swap_test",
            "htlc_implementation": "_execute_htlc_implementation"
        }

    async def route_operation(self, message: Message) -> bool:
        """Route operation to appropriate handler"""
        try:
            operation_type = await self.detector.detect_operation_type(message.content)
            logger.info(f"🎯 Detected operation: {operation_type}")
            
            handler_name = self.operation_handlers.get(operation_type)
            if handler_name and hasattr(self.agent, handler_name):
                handler = getattr(self.agent, handler_name)
                return await handler(message)
            else:
                # Fallback to parent class tool calling
                return await self.agent._fallback_operation(message)
                
        except Exception as e:
            logger.error(f"❌ Operation routing failed: {e}")
            await self.agent._send_error_response(message, e)
            return False

    def parse_swap_request(self, content: str) -> SwapRequest:
        """Parse swap request from natural language"""
        content_lower = content.lower()
        
        # Simple parsing logic - can be enhanced with NLP
        from_currency = "ETH" if "eth" in content_lower else "DOGE"
        to_currency = "DOGE" if from_currency == "ETH" else "ETH"
        
        # Extract amount (basic regex pattern)
        import re
        amount_pattern = r'(\d+\.?\d*)\s*(?:eth|doge|dollars?|\$)'
        amount_match = re.search(amount_pattern, content_lower)
        amount = float(amount_match.group(1)) if amount_match else 0.1
        
        # Extract conditions
        conditions = {}
        if "when" in content_lower:
            conditions["conditional"] = True
            if "good" in content_lower:
                conditions["timing"] = "optimal"
            if "not if" in content_lower:
                conditions["avoid_conditions"] = True
        
        return SwapRequest(
            from_currency=from_currency,
            to_currency=to_currency,
            from_amount=amount,
            conditions=conditions if conditions else None
        )


class ConversationalDeFiHandler:
    """Handles conversational DeFi operations with orchestration"""
    
    def __init__(self, agent_instance):
        self.agent = agent_instance

    async def execute_conversational_defi(self, message: Message) -> OperationResult:
        """Execute conversational DeFi request using orchestration engine"""
        try:
            if not ORCHESTRATION_AVAILABLE:
                return OperationResult(
                    success=False,
                    operation_type="conversational_defi",
                    message="Orchestration engine not available"
                )

            logger.info("🎭 Executing conversational DeFi operation...")
            
            # Process with orchestration engine
            orchestration_result = await process_conversational_request(
                user_input=message.content,
                context={
                    "agent": "dogesmartx_agent", 
                    "operation": "conversational_defi",
                    "timestamp": asyncio.get_event_loop().time()
                }
            )
            
            if orchestration_result.get("success"):
                # Format successful orchestration result
                response = f"""🎭 **Intelligent DogeSmartX Operation Completed**
════════════════════════════════════════════════════════════

🧠 **AI-Powered Execution**: {orchestration_result.get('plan_description', 'Intelligent DeFi coordination')}
⚡ **Orchestration Result**: {orchestration_result.get('execution_result', {}).get('message', 'Operation coordinated successfully')}

🔄 **Enhanced with:**
• Multi-agent coordination
• Market timing analysis
• Optimal execution conditions
• Real atomic swap capabilities

{self._format_orchestration_result(orchestration_result.get('execution_result', {}))}

✨ **This demonstrates the future of conversational DeFi automation!**
"""
                
                return OperationResult(
                    success=True,
                    operation_type="conversational_defi",
                    message=response,
                    data=orchestration_result,
                    agent_used="orchestration_engine"
                )
            else:
                return OperationResult(
                    success=False,
                    operation_type="conversational_defi", 
                    message="Orchestration failed",
                    data=orchestration_result
                )
                
        except Exception as e:
            logger.error(f"❌ Conversational DeFi execution failed: {e}")
            return OperationResult(
                success=False,
                operation_type="conversational_defi",
                message=f"Execution failed: {str(e)}"
            )

    def _format_orchestration_result(self, execution_result: Dict[str, Any]) -> str:
        """Format orchestration execution result for display"""
        if not execution_result:
            return ""
            
        formatted_lines = []
        
        if execution_result.get("agents_used"):
            formatted_lines.append(f"🤖 **Agents Used**: {', '.join(execution_result['agents_used'])}")
        
        if execution_result.get("execution_time"):
            formatted_lines.append(f"⏱️ **Execution Time**: {execution_result['execution_time']:.2f}s")
        
        if execution_result.get("user_experience"):
            formatted_lines.append(f"🌟 **Experience**: {execution_result['user_experience']}")
        
        return "\n".join(formatted_lines) if formatted_lines else "Operation completed successfully"
