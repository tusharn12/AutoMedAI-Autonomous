from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

# Get the application logger instance
logger = logging.getLogger("AutoMedAI_FastAPI")

class AgentInterface(ABC):
    """
    Abstract Base Class for all specialist agents.
    Ensures that each agent implements a query method.
    """
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        # Create a child logger for this specific agent
        self.logger = logging.getLogger(f"AutoMedAI_FastAPI.{self.agent_name}")
        self.state: Dict[str, Any] = {}

    @abstractmethod
    def query(self, symptoms: str, patient_id: str, **kwargs) -> dict:
        """
        Processes the patient's symptoms and returns a diagnostic hypothesis.

        Args:
            symptoms (str): The patient's reported symptoms.
            patient_id (str): The unique ID for the patient/request for logging.
            **kwargs: Additional context or parameters specific to an agent.

        Returns:
            dict: A dictionary containing the agent's findings.
                  Example: {
                      "agent_name": self.agent_name,
                      "hypothesis": "...",
                      "confidence": 0.0,
                      "details": "..."
                  }
        """
        pass

    def log_interaction(self, patient_id: str, input_data: any, output_data: any, level: str = "info"):
        """
        Helper method for consistent logging.
        
        Args:
            patient_id (str): The unique ID for the patient/request
            input_data (any): The input data received by the agent
            output_data (any): The output data produced by the agent
            level (str): Log level (info, error, debug)
        """
        log_message = f"Interaction for patient_id: {patient_id}"
        extra_info = {
            "patient_id": patient_id,
            "agent_name": self.agent_name,
            "input": input_data,
            "output": output_data
        }
        
        if level.lower() == "info":
            self.logger.info(log_message, extra=extra_info)
        elif level.lower() == "error":
            self.logger.error(log_message, extra=extra_info, exc_info=True)
        elif level.lower() == "debug":
            self.logger.debug(log_message, extra=extra_info)

    def update_state(self, new_state: Dict[str, Any]) -> None:
        """
        Update the agent's internal state.
        
        Args:
            new_state: Dictionary containing state updates
        """
        self.state.update(new_state)
        self.logger.debug(
            f"Agent state updated",
            extra={
                "agent_name": self.agent_name,
                "state_update": new_state
            }
        )
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get the current state of the agent.
        
        Returns:
            Dictionary containing the agent's current state
        """
        return self.state.copy()
    
    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the agent's resources and connections.
        Should be called before the agent starts processing.
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """
        Clean up the agent's resources.
        Should be called when the agent is being shut down.
        """
        pass
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.agent_name})" 