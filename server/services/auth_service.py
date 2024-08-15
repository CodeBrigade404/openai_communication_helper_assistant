from server.utils.mongodb_client import db
import hashlib
from fastapi_jwt_auth import AuthJWT
from server.models.user import User, UserLogin

async def register_user(user: User):
    # Check for missing fields
    if not all([user.username, user.password, user.names.get('f_name'), user.names.get('l_name'), user.birth_date, user.address, user.mobile_number, user.about_me]):
        return {"error": "Please provide all required fields"}, 400

    # Check for existing user
    existing_user = db.users.find_one({'username': user.username})
    if existing_user:
        return {"error": "Username already taken"}, 400

    # Hash the password
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()

    # Create new user
    new_user = user.dict()
    new_user['password'] = hashed_password
    db.users.insert_one(new_user)
    return {"message": "Registration successful!"}, 201

async def authenticate_user(user: UserLogin):
    # Check for missing fields
    if not user.username or not user.password:
        return {"error": "Username and password are required"}, 400

    # Verify user credentials
    user_doc = db.users.find_one({'username': user.username})
    if not user_doc:
        return {"error": "User not found"}, 404

    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    if user_doc['password'] != hashed_password:
        return {"error": "Invalid password"}, 401

    # Generate JWT token
    access_token = AuthJWT.create_access_token(identity=user.username)
    return {"access_token": access_token}, 200
