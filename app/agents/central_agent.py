from typing import Dict, Any, List, Type
import asyncio
import logging
import json
from .base_agent import AgentInterface
from .specialist_agents import (
    SpecialistAgent, GeneralPractitionerAgent, EmergencyMedicineAgent,
    CardioBotMock, NeuroBotMock, OrthoBotMock
)

logger = logging.getLogger("AutoMedAI_FastAPI.CentralReasoningAgentMock")

class CentralReasoningAgentMock:
    """Mock agent for synthesizing findings from specialist agents."""
    
    def __init__(self):
        self.agent_name = "CentralReasoningAgentMock"
        # In a real scenario, this agent would use an LLM (e.g., GPT via LangChain)
        # For Phase 2, it's a simple rule-based aggregator.

    def synthesize_findings(self, patient_symptoms: str, specialist_findings: list, patient_id: str) -> dict:
        """
        Combines findings from specialist agents into a summary.
        In Phase 2, this is a very basic aggregation.

        Args:
            patient_symptoms (str): The original patient symptoms.
            specialist_findings (list): A list of dictionaries, where each dict is an output from a specialist agent.
            patient_id (str): The unique ID for the patient/request.

        Returns:
            dict: A dictionary containing the synthesized report.
        """
        logger.info(
            "Synthesizing findings", 
            extra={
                "patient_id": patient_id,
                "agent_name": self.agent_name,
                "symptoms_received": patient_symptoms,
                "num_specialist_reports": len(specialist_findings)
            }
        )

        summary_parts = [f"Central Reasoning Mock Summary for Patient ID: {patient_id}"]
        summary_parts.append(f"Original Symptoms: {patient_symptoms}")
        summary_parts.append("\n--- Specialist Agent Reports ---")

        if not specialist_findings:
            summary_parts.append("No specialist agent reports were provided.")
        else:
            for finding in specialist_findings:
                agent_name = finding.get("agent_name", "UnknownAgent")
                hypothesis = finding.get("hypothesis", "No hypothesis provided.")
                # Try to get confidence from either key
                confidence = finding.get("confidence")
                if confidence is None:
                    confidence = finding.get("confidence_mock", "N/A")
                details = finding.get("details", "")
                summary_parts.append(
                    f"\nReport from {agent_name}:\n"
                    f"  Hypothesis: {hypothesis}\n"
                    f"  Confidence: {confidence}\n"  # Removed "Mock" prefix since it could be either type
                    f"  Details: {details}"
                )
        
        final_summary = "\n".join(summary_parts)
        
        # Mock triage recommendation
        triage_recommendation = "Mock Triage: Review by a human telemedicine provider is recommended."
        if any("chest pain" in finding.get("hypothesis", "").lower() for finding in specialist_findings if finding.get("agent_name") == "CardioBotMock"):
            triage_recommendation = "Mock Triage: Potential cardiac concern noted. Prioritize human review."

        result = {
            "patient_id": patient_id,
            "overall_summary": final_summary,
            "consolidated_hypotheses_mock": "Multiple mock hypotheses - see summary.",
            "triage_recommendation_mock": triage_recommendation,
            "confidence_overall_mock": 0.1,  # Very low for mock system
            "notes": "This is a mock synthesis from Phase 2. LLM reasoning will be added later."
        }
        
        logger.info(
            "Synthesis complete", 
            extra={
                "patient_id": patient_id,
                "agent_name": self.agent_name,
                "summary_generated": result["overall_summary"][:200] + "..."  # Log a snippet
            }
        )
        return result

class CentralAgent(AgentInterface):
    """
    Central coordinating agent that manages specialist agents and orchestrates the diagnosis process.
    """
    
    def __init__(self):
        super().__init__(agent_name="central-coordinator")
        self.specialist_agents: Dict[str, AgentInterface] = {}
        self.reasoning_agent = CentralReasoningAgentMock()
        self.state.update({
            "active_specialists": [],
            "cases_in_progress": 0,
            "total_cases_handled": 0
        })

    async def initialize(self) -> None:
        """Initialize the central agent and its specialist agents."""
        self.logger.info(
            "Initializing Central Coordinator Agent",
            extra={"active_specialists": []}
        )
        
        # Initialize core agents
        await self._initialize_specialist(GeneralPractitionerAgent)
        await self._initialize_specialist(EmergencyMedicineAgent)
        
        # Initialize mock specialist agents
        await self._initialize_specialist(CardioBotMock)
        await self._initialize_specialist(NeuroBotMock)
        await self._initialize_specialist(OrthoBotMock)
        
        self.state["active_specialists"] = list(self.specialist_agents.keys())
        self.logger.info(
            "Central agent initialization complete",
            extra={"active_specialists": self.state["active_specialists"]}
        )

    async def cleanup(self) -> None:
        """Cleanup all managed specialist agents."""
        self.logger.info(
            "Cleaning up Central Coordinator Agent",
            extra={
                "total_cases": self.state["total_cases_handled"],
                "active_specialists": self.state["active_specialists"]
            }
        )
        
        cleanup_tasks = [
            agent.cleanup() 
            for agent in self.specialist_agents.values()
        ]
        await asyncio.gather(*cleanup_tasks)
        self.specialist_agents.clear()
        self.state["active_specialists"] = []

    async def _initialize_specialist(self, specialist_class: Type[AgentInterface]) -> None:
        """
        Initialize a new specialist agent of the given class.
        
        Args:
            specialist_class: The specialist agent class to initialize
        """
        specialist = specialist_class()
        await specialist.initialize()
        self.specialist_agents[specialist.agent_name] = specialist
        
        self.logger.info(
            "Specialist agent initialized",
            extra={
                "agent_name": specialist.agent_name
            }
        )

    def query(self, symptoms: str, patient_id: str, **kwargs) -> dict:
        """
        Process a new case by coordinating with specialist agents.
        
        Args:
            symptoms: The patient's reported symptoms
            patient_id: Unique identifier for the patient/request
            **kwargs: Additional parameters for specialist agents
            
        Returns:
            Dictionary containing aggregated diagnosis and recommendations
        """
        self.state["cases_in_progress"] += 1
        
        try:
            # Log the incoming request
            self.log_interaction(
                patient_id=patient_id,
                input_data={"symptoms": symptoms, **kwargs},
                output_data=None,
                level="debug"
            )
            
            # First, get initial assessment from GP
            gp = next((agent for agent in self.specialist_agents.values() 
                      if isinstance(agent, GeneralPractitionerAgent)), None)
            if not gp:
                error_msg = "No General Practitioner agent available"
                self.logger.error(
                    error_msg,
                    extra={"patient_id": patient_id}
                )
                raise ValueError(error_msg)
            
            # Get GP assessment
            initial_assessment = gp.query(symptoms, patient_id, **kwargs)
            
            # Get assessments from all mock specialists
            specialist_assessments = []
            for agent in self.specialist_agents.values():
                if isinstance(agent, (CardioBotMock, NeuroBotMock, OrthoBotMock)):
                    assessment = agent.query(symptoms, patient_id, **kwargs)
                    specialist_assessments.append(assessment)
            
            # Check if emergency care is needed
            if initial_assessment.get("needs_emergency_care", False):
                emergency = next((agent for agent in self.specialist_agents.values() 
                                if isinstance(agent, EmergencyMedicineAgent)), None)
                if emergency:
                    emergency_assessment = emergency.query(symptoms, patient_id, **kwargs)
                    specialist_assessments.append(emergency_assessment)
            
            # Synthesize findings using the reasoning agent
            synthesis = self.reasoning_agent.synthesize_findings(
                patient_symptoms=symptoms,
                specialist_findings=specialist_assessments,
                patient_id=patient_id
            )
            
            # Prepare final response
            response = {
                "case_id": patient_id,
                "initial_assessment": initial_assessment,
                "specialist_assessments": specialist_assessments,
                "synthesis": synthesis,
                "coordinating_agent": self.agent_name
            }
            
            # Log the final response
            self.log_interaction(
                patient_id=patient_id,
                input_data={"symptoms": symptoms},
                output_data=response,
                level="info"
            )
            
            self.state["total_cases_handled"] += 1
            return response
            
        finally:
            self.state["cases_in_progress"] -= 1
    
    def get_active_specialists(self) -> List[str]:
        """Get list of currently active specialist agents."""
        return self.state["active_specialists"]
    
    async def add_specialist(self, specialist_class: Type[AgentInterface]) -> None:
        """
        Add a new specialist agent to the system.
        
        Args:
            specialist_class: The specialist agent class to add
        """
        await self._initialize_specialist(specialist_class)
        self.state["active_specialists"] = list(self.specialist_agents.keys()) 