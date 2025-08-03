"""
Base Agent Module for DogeSmartX Orchestration Engine
Provides the foundation for all specialized agents
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field

from app.logger import logger


class AgentCapability(BaseModel):
    """Defines what an agent can do"""
    name: str
    description: str
    required_inputs: List[str] = Field(default_factory=list)
    optional_inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    execution_time_estimate: float = Field(default=1.0)  # seconds


class AgentTask(BaseModel):
    """Represents a task assigned to an agent"""
    task_id: str
    agent_name: str
    capability: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=5)  # 1-10, 10 being highest
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="pending")  # pending, running, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BaseAgentModule(ABC):
    """
    Base class for all DogeSmartX agent modules
    Provides common functionality and interface
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.capabilities: Dict[str, AgentCapability] = {}
        self.is_active = True
        self.current_task: Optional[AgentTask] = None
        self.task_queue: List[AgentTask] = []
        self.performance_metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_execution_time": 0.0,
            "success_rate": 0.0
        }
        
        # Initialize capabilities
        self._register_capabilities()
        
        logger.info(f"🤖 {self.name} agent initialized with {len(self.capabilities)} capabilities")
    
    @abstractmethod
    def _register_capabilities(self):
        """Register the capabilities this agent provides"""
        pass
    
    @abstractmethod
    async def execute_capability(self, capability_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific capability"""
        pass
    
    def register_capability(self, capability: AgentCapability):
        """Register a new capability"""
        self.capabilities[capability.name] = capability
        logger.debug(f"📋 {self.name}: Registered capability '{capability.name}'")
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Get all available capabilities"""
        return list(self.capabilities.values())
    
    def can_handle(self, capability_name: str) -> bool:
        """Check if this agent can handle a specific capability"""
        return capability_name in self.capabilities
    
    async def execute_task(self, task: AgentTask) -> AgentTask:
        """Execute a task and return the updated task with results"""
        if not self.can_handle(task.capability):
            task.status = "failed"
            task.error = f"Agent {self.name} cannot handle capability '{task.capability}'"
            return task
        
        self.current_task = task
        task.status = "running"
        start_time = datetime.now()
        
        try:
            logger.info(f"🚀 {self.name}: Starting task {task.task_id} ({task.capability})")
            
            # Execute the capability
            result = await self.execute_capability(task.capability, task.inputs)
            
            # Update task with results
            task.result = result
            task.status = "completed"
            
            # Update performance metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_metrics(execution_time, success=True)
            
            logger.info(f"✅ {self.name}: Completed task {task.task_id} in {execution_time:.2f}s")
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_metrics(execution_time, success=False)
            
            logger.error(f"❌ {self.name}: Task {task.task_id} failed: {e}")
        
        finally:
            self.current_task = None
        
        return task
    
    def _update_performance_metrics(self, execution_time: float, success: bool):
        """Update agent performance metrics"""
        if success:
            self.performance_metrics["tasks_completed"] += 1
        else:
            self.performance_metrics["tasks_failed"] += 1
        
        total_tasks = self.performance_metrics["tasks_completed"] + self.performance_metrics["tasks_failed"]
        
        # Update average execution time
        current_avg = self.performance_metrics["average_execution_time"]
        self.performance_metrics["average_execution_time"] = (
            (current_avg * (total_tasks - 1) + execution_time) / total_tasks
        )
        
        # Update success rate
        self.performance_metrics["success_rate"] = (
            self.performance_metrics["tasks_completed"] / total_tasks * 100
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "current_task": self.current_task.dict() if self.current_task else None,
            "queue_length": len(self.task_queue),
            "capabilities": [cap.name for cap in self.capabilities.values()],
            "performance": self.performance_metrics
        }
    
    async def initialize(self) -> bool:
        """Initialize the agent (override in subclasses if needed)"""
        return True
    
    async def shutdown(self):
        """Shutdown the agent gracefully"""
        self.is_active = False
        logger.info(f"🔴 {self.name} agent shutting down")


class AgentCommunication:
    """Handles communication between agents"""
    
    def __init__(self):
        self.message_queue: List[Dict[str, Any]] = []
    
    async def send_message(self, from_agent: str, to_agent: str, message_type: str, data: Dict[str, Any]):
        """Send a message between agents"""
        message = {
            "from": from_agent,
            "to": to_agent,
            "type": message_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.message_queue.append(message)
        logger.debug(f"📨 Message: {from_agent} → {to_agent} ({message_type})")
    
    async def get_messages(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get messages for a specific agent"""
        messages = [msg for msg in self.message_queue if msg["to"] == agent_name]
        # Remove retrieved messages
        self.message_queue = [msg for msg in self.message_queue if msg["to"] != agent_name]
        return messages
