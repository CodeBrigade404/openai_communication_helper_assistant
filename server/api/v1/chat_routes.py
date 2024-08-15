from fastapi import APIRouter, HTTPException
from server.models.chat import ChatRequest
from server.services.chat_service import handle_chat

router = APIRouter()

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = await handle_chat(request.session_id, request.user_message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
