from fastapi import APIRouter
from server.models.user import User, UserLogin
from server.services.auth_service import register_user, authenticate_user

router = APIRouter()


@router.post("/sign_up")
async def sign_up(user: User):
    response = await register_user(user)
    return response


@router.post("/sign_in")
async def sign_in(user: UserLogin):
    response = authenticate_user(user)
    return response
