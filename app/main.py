from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .agents.central_agent import CentralAgent  # Updated import
from .core.logging_config import setup_logging
import uuid
import os

# Setup logging with Loki URL from environment
loki_url = os.getenv('LOKI_URL')
logger = setup_logging(loki_url=loki_url)

# Create and initialize the central agent
central_agent = CentralAgent()

# Create FastAPI app
app = FastAPI(
    title="AutoMedAI",
    description="AutoMedAI - Autonomous Medical AI System",
    version="0.2.0"  # Updated for Phase 2
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting AutoMedAI application - Phase 2: Hierarchical Agent Architecture")
    # Initialize the central agent
    await central_agent.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down AutoMedAI application")
    # Cleanup the central agent
    await central_agent.cleanup()

@app.get("/health", tags=["Utility"])
async def health_check():
    active_specialists = central_agent.get_active_specialists()
    logger.info("Health check endpoint called", extra={"active_specialists": active_specialists})
    return {
        "status": "healthy",
        "message": "AutoMedAI is running with Phase 2 Agent Architecture!",
        "active_specialists": active_specialists
    }

@app.post("/diagnose", tags=["Diagnosis"])
async def diagnose_patient(
    patient_symptoms: str = Form(...)
):
    patient_id = str(uuid.uuid4())
    
    initial_log_extra = {
        "patient_id": patient_id,
        "symptoms_length": len(patient_symptoms)
    }
    logger.info(
        f"Phase 2: Diagnosis request received for symptoms: '{patient_symptoms[:100]}...'",
        extra=initial_log_extra
    )

    try:
        # Use the central agent to handle the entire diagnosis process
        final_report = central_agent.query(
            symptoms=patient_symptoms,
            patient_id=patient_id
        )
        
        logger.info(
            "Phase 2: Diagnosis process complete",
            extra={
                "patient_id": patient_id,
                "synthesis_generated": bool(final_report.get("synthesis")),
                "num_specialist_assessments": len(final_report.get("specialist_assessments", [])),
                "triage_recommendation": final_report.get("synthesis", {}).get("triage_recommendation_mock", "N/A")
            }
        )
        
        return final_report
        
    except Exception as e:
        logger.error(
            f"Error processing diagnosis request",
            exc_info=True,
            extra={
                "patient_id": patient_id,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=500,
            detail={
                "patient_id": patient_id,
                "error": "Failed to process diagnosis request due to an internal error.",
                "details": str(e)
            }
        ) 