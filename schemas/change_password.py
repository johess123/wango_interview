# from pydantic import BaseModel, Field

# class Password(BaseModel):
#     original_password: str = Field(max_length=20)
#     new_password: str = Field(max_length=20)
#     model_config = {
#         "json_schema_extra": {
#             "examples": [
#                 {
#                     "original_password": "123456",
#                     "new_password": "654321"
#                 }
#             ]
#         }
#     }