from pydantic import BaseModel, Field

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