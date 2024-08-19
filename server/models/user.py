from pydantic import BaseModel, Field
from typing import Optional, Dict

class User(BaseModel):
    username: str
    password: str
    names: Dict[str, Optional[str]] = Field(default_factory=dict)
    birth_date: str
    address: str
    mobile_number: str
    guardian_mobile_number: Optional[str] = None
    email: Optional[str] = None
    about_me: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "password123",
                "names": {
                    "f_name": "John",
                    "l_name": "Doe",
                    "surname": "Smith",
                    "nick_name": "Johnny"
                },
                "birth_date": "1990-01-01",
                "address": "123 Main St",
                "mobile_number": "+1234567890",
                "guardian_mobile_number": "+0987654321",
                "email": "john.doe@example.com",
                "about_me": "Software developer from New York."
            }
        }

class UserLogin(BaseModel):
    username: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "password123"
            }
        }
