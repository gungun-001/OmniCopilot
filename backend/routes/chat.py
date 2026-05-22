from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agents.orchestrator import stream_agent_handler
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_session"
    attached_file_name: Optional[str] = None
    attached_file_content: Optional[str] = None

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Receives file uploads, extracts their text content (handling PDFs and text/code files),
    and returns the filename and parsed text.
    """
    filename = file.filename
    try:
        content = await file.read()
        text_content = ""
        
        # 1. Parse PDF files
        if filename.lower().endswith(".pdf"):
            import io
            from pypdf import PdfReader
            pdf_file = io.BytesIO(content)
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            text_content = text
            
        # 2. Parse text/code/csv/json files
        else:
            try:
                text_content = content.decode("utf-8")
            except UnicodeDecodeError:
                text_content = content.decode("latin-1")
                
        return {"filename": filename, "content": text_content}
    except Exception as e:
        logger.error(f"Error parsing file {filename}: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to read or parse file: {str(e)}")

@router.post("")
async def chat_endpoint(request: ChatRequest):
    """
    Unified chat endpoint that returns a real-time stream of agent events.
    """
    logger.info(f"Incoming chat request for session: {request.session_id}")
    
    # Prepend the file content as a system note for the AI orchestrator
    message_to_send = request.message
    if request.attached_file_name and request.attached_file_content:
        message_to_send = (
            f"[SYSTEM NOTE: The user has uploaded an attached file named '{request.attached_file_name}'. "
            f"Here is the parsed content of the file for analysis:\n"
            f"--- START OF FILE CONTENT ---\n"
            f"{request.attached_file_content}\n"
            f"--- END OF FILE CONTENT ---\n"
            f"Please analyze the file content above and use it to help answer the user's request: '{request.message}']"
        )
        
    return StreamingResponse(
        stream_agent_handler(message_to_send, request.session_id),
        media_type="text/event-stream"
    )
