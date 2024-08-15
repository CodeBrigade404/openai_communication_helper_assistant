from fastapi import APIRouter, HTTPException, Depends
from server.models.user import User, UserLogin
from server.services.auth_service import register_user, authenticate_user
from fastapi_jwt_auth import AuthJWT

router = APIRouter()

@router.post("/sign_up")
async def sign_up(user: User):
    response = await register_user(user)
    return response

@router.post("/sign_in")
async def sign_in(user: UserLogin, auth_jwt: AuthJWT = Depends()):
    response = await authenticate_user(user, auth_jwt)
    return response
