from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agents.orchestrator import stream_agent_handler
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_session"

@router.post("")
async def chat_endpoint(request: ChatRequest):
    """
    Unified chat endpoint that returns a real-time stream of agent events.
    """
    logger.info(f"Incoming chat request for session: {request.session_id}")
    
    return StreamingResponse(
        stream_agent_handler(request.message, request.session_id),
        media_type="text/event-stream"
    )


