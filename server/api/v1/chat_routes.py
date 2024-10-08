from fastapi import APIRouter, HTTPException, Depends, status
from server.models.chat import ChatRequest
from server.services.chat_service import handle_chat
from server.utils.jwt_utils import jwt_required

router = APIRouter()

@router.post("/chat")
async def chat(request: ChatRequest, token_data: dict = Depends(jwt_required)):
    try:
        response = await handle_chat(request,token_data)
        return response
    except Exception as e:
        HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
