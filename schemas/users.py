from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    username: str = Field(max_length=10)
    password: str = Field(max_length=20)
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "kenny",
                    "password": "123456"
                }
            ]
        }
    }

class UserResponse(BaseModel):
    id: int
    name: str
    image_count: int

class UserResponseWrapper(BaseModel):
    data: UserResponse
    new_access_token: Optional[str] = None

class ChangePassword(BaseModel):
    original_password: str = Field(max_length=20)
    new_password: str = Field(max_length=20)
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "original_password": "123456",
                    "new_password": "654321"
                }
            ]
        }
    }

