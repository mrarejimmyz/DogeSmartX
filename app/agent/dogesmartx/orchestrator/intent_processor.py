"""
DogeSmartX Intent Processor
Natural language processing for user intent classification.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging


class IntentProcessor:
    """Process and classify user intents for DogeSmartX operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.intent_patterns = self._initialize_patterns()
        self.entity_extractors = self._initialize_extractors()
    
    def _initialize_patterns(self) -> Dict[str, List[str]]:
        """Initialize intent classification patterns"""
        return {
            "swap_request": [
                r"swap\s+(\d+(?:\.\d+)?)\s+(eth|doge)\s+(?:to|for)\s+(eth|doge)",
                r"exchange\s+(\d+(?:\.\d+)?)\s+(eth|doge)",
                r"trade\s+(\d+(?:\.\d+)?)\s+(eth|doge)",
                r"convert\s+(\d+(?:\.\d+)?)\s+(eth|doge)"
            ],
            "price_query": [
                r"(?:what(?:'s| is)? the )?price (?:of )?(eth|doge|ethereum|dogecoin)",
                r"how much (?:is )?(eth|doge|ethereum|dogecoin)",
                r"current (?:value|price) (?:of )?(eth|doge|ethereum|dogecoin)"
            ],
            "balance_query": [
                r"(?:what(?:'s| is)? my )?balance",
                r"how much (?:do i have|eth|doge)",
                r"check (?:my )?wallet"
            ],
            "market_analysis": [
                r"market (?:analysis|conditions|sentiment)",
                r"should i (?:swap|trade|buy|sell)",
                r"best time to (?:swap|trade)"
            ],
            "help_request": [
                r"help", r"what can you do", r"capabilities",
                r"how (?:do|can) i", r"explain"
            ]
        }
    
    def _initialize_extractors(self) -> Dict[str, callable]:
        """Initialize entity extraction functions"""
        return {
            "amount": self._extract_amount,
            "currency": self._extract_currency,
            "timeframe": self._extract_timeframe,
            "address": self._extract_address
        }
    
    async def process_intent(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user message and extract intent with entities"""
        try:
            message_clean = message.lower().strip()
            
            # Classify primary intent
            intent = await self._classify_intent(message_clean)
            
            # Extract entities
            entities = await self._extract_entities(message_clean, intent)
            
            # Calculate confidence
            confidence = await self._calculate_confidence(message_clean, intent, entities)
            
            return {
                "intent": intent,
                "entities": entities,
                "confidence": confidence,
                "original_message": message,
                "processed_at": datetime.utcnow().isoformat(),
                "context": context or {}
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process intent: {e}")
            return {
                "intent": "unknown",
                "entities": {},
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def _classify_intent(self, message: str) -> str:
        """Classify the primary intent of the message"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    return intent
        
        return "general_inquiry"
    
    async def _extract_entities(self, message: str, intent: str) -> Dict[str, Any]:
        """Extract relevant entities from the message"""
        entities = {}
        
        for entity_type, extractor in self.entity_extractors.items():
            try:
                value = extractor(message)
                if value:
                    entities[entity_type] = value
            except Exception as e:
                self.logger.warning(f"Failed to extract {entity_type}: {e}")
        
        return entities
    
    def _extract_amount(self, message: str) -> Optional[float]:
        """Extract numeric amounts from message"""
        patterns = [
            r"(\d+(?:\.\d+)?)\s*(?:eth|doge)",
            r"(\d+(?:\.\d+)?)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    def _extract_currency(self, message: str) -> Optional[List[str]]:
        """Extract currency mentions from message"""
        currencies = []
        currency_patterns = {
            "eth": r"\b(?:eth|ethereum)\b",
            "doge": r"\b(?:doge|dogecoin)\b"
        }
        
        for currency, pattern in currency_patterns.items():
            if re.search(pattern, message, re.IGNORECASE):
                currencies.append(currency)
        
        return currencies if currencies else None
    
    def _extract_timeframe(self, message: str) -> Optional[str]:
        """Extract timeframe mentions from message"""
        timeframe_patterns = {
            "now": r"\b(?:now|immediately|asap)\b",
            "today": r"\b(?:today|this day)\b",
            "hour": r"(\d+)\s*hours?",
            "minute": r"(\d+)\s*minutes?"
        }
        
        for timeframe, pattern in timeframe_patterns.items():
            if re.search(pattern, message, re.IGNORECASE):
                return timeframe
        
        return None
    
    def _extract_address(self, message: str) -> Optional[str]:
        """Extract wallet addresses from message"""
        # Ethereum address pattern
        eth_pattern = r"\b0x[a-fA-F0-9]{40}\b"
        eth_match = re.search(eth_pattern, message)
        if eth_match:
            return eth_match.group(0)
        
        # Dogecoin address pattern (simplified)
        doge_pattern = r"\b[DA9][1-9A-HJ-NP-Za-km-z]{25,34}\b"
        doge_match = re.search(doge_pattern, message)
        if doge_match:
            return doge_match.group(0)
        
        return None
    
    async def _calculate_confidence(self, message: str, intent: str, entities: Dict[str, Any]) -> float:
        """Calculate confidence score for the intent classification"""
        base_confidence = 0.7
        
        # Increase confidence if entities are found
        if entities:
            base_confidence += 0.1 * len(entities)
        
        # Increase confidence for specific intents with clear patterns
        if intent in ["swap_request", "price_query"] and entities.get("currency"):
            base_confidence += 0.15
        
        return min(1.0, base_confidence)
