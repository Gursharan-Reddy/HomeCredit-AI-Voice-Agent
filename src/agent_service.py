"""
FastAPI Backend Service for Voice Agent Integration (Retell / Bolna webhook handler)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from src.prompt_template import get_system_prompt
from src.state_machine import QualificationState

app = FastAPI(title="Home Credit LAP Voice Agent API", version="1.0.0")

class AgentRequest(BaseModel):
    call_id: str
    customer_name: str
    agent_name: Optional[str] = "Priya"
    agent_gender: Optional[str] = "Female"
    language_to_speak: Optional[str] = "English"
    current_date: Optional[str] = "2026-10-09"
    current_day: Optional[str] = "Friday"
    current_time: Optional[str] = "12:00 PM"
    additional_context_from_rag: Optional[str] = ""
    customer_utterance: Optional[str] = ""
    extracted_data: Optional[Dict[str, Any]] = {}

@app.post("/initialize-agent")
def initialize_agent(req: AgentRequest):
    prompt = get_system_prompt(req.dict())
    return {
        "status": "success",
        "system_prompt": prompt,
        "initial_greeting": f"Hello, may I please speak with {req.customer_name}?"
    }

@app.post("/process-turn")
def process_turn(req: AgentRequest):
    state = QualificationState()
    state.update_from_utterance(req.extracted_data)
    
    if state.disqualified:
        return {
            "action": "end_call",
            "message": "We regret to inform you that based on your details, you do not meet the criteria for this specific offer at this time. Thank you for your time with Home Credit."
        }
    
    if state.transfer_required or state.existing_property_loan:
        return {
            "action": "end_call",
            "message": "Since you have an existing loan or EMI transfer request, our loan-transfer specialist will contact you shortly. Thank you!"
        }
        
    next_q = state.get_first_missing_question()
    if not next_q:
        return {
            "action": "handoff_to_expert",
            "message": "Thank you for providing all details. You are provisionally qualified! A senior loan expert will call you back shortly with exact interest rates."
        }
        
    return {
        "action": "continue",
        "next_checklist_item": next_q
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)