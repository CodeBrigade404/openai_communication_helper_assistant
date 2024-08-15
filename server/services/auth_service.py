import hashlib
import jwt
from server.utils.mongodb_client import db
from server.models.user import User , UserLogin
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime ,timedelta



async def register_user(user: User):
    # Check for missing fields
    if not all([user.username, user.password, user.names.get('f_name'), user.names.get('l_name'), user.birth_date, user.address, user.mobile_number, user.about_me]):
        return JSONResponse(content={"message": "Please provide all required fields"}, status_code=400)

    # Check for existing user
    existing_user = db.users.find_one({'username': user.username})
    if existing_user:
        return JSONResponse(content={"message": "Username already taken"}, status_code=400)

    # Hash the password
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()

    # Create new user
    new_user = user.model_dump()
    new_user['password'] = hashed_password
    db.users.insert_one(new_user)
    return JSONResponse(content={"message": "Registration successful!"}, status_code=201)


def authenticate_user(user: UserLogin):
    # Check for missing fields
    if not user.username or not user.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username and password are required")

    # Verify user credentials
    user_doc = db.users.find_one({'username': user.username})
    if not user_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    if user_doc['password'] != hashed_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    # Create access token
    encoded_jwt = jwt.encode({"id": user.username, "exp": datetime.now() + timedelta(minutes=15)}, "secret", algorithm="HS256")

    return {"access_token": encoded_jwt}
