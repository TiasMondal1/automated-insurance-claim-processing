"""Base agent class for all agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
from datetime import datetime

from utils.llm_provider import LLMProvider, get_llm_provider


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(
        self,
        agent_name: str,
        llm_provider: Optional[LLMProvider] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize base agent.
        
        Args:
            agent_name: Name of the agent
            llm_provider: LLM provider instance
            logger: Logger instance
        """
        self.agent_name = agent_name
        self.llm_provider = llm_provider or get_llm_provider()
        self.logger = logger or self._setup_logger()
        self.execution_history = []
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for the agent."""
        logger = logging.getLogger(self.agent_name)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return results.
        
        Args:
            input_data: Input data for processing
            
        Returns:
            Processing results
        """
        pass
    
    def log_execution(self, input_data: Dict[str, Any], output_data: Dict[str, Any], duration: float):
        """
        Log execution details.
        
        Args:
            input_data: Input data
            output_data: Output data
            duration: Execution duration in seconds
        """
        execution_record = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_name,
            "duration_seconds": duration,
            "status": output_data.get("status", "unknown")
        }
        self.execution_history.append(execution_record)
        
        self.logger.info(
            f"{self.agent_name} completed in {duration:.2f}s - Status: {execution_record['status']}"
        )
    
    def get_system_prompt(self) -> str:
        """
        Get system prompt for the agent.
        
        Returns:
            System prompt string
        """
        return f"You are {self.agent_name}, an AI agent specialized in insurance claim processing."
