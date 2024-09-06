from fastapi import APIRouter, HTTPException, Depends, status
from server.utils.jwt_utils import jwt_required
from server.utils.mongodb_client import get_user_details

router = APIRouter()

@router.get("/user")
async def get_user(token_data: dict = Depends(jwt_required)):
    user_info = get_user_details(token_data["username"])
    if "error" in user_info:
        raise HTTPException(status_code=404, detail=user_info["error"])
    return user_info