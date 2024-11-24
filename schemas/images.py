from pydantic import BaseModel
from typing import List, Optional

class ImageResponse(BaseModel):
    id: int
    file_name: str
    file_path: str
    text: str
    user_id: int

class ImageResponseWrapper(BaseModel):
    data: ImageResponse
    new_access_token: Optional[str] = None

class ImageListResponse(BaseModel):
    data: List[ImageResponse]
    new_access_token: Optional[str] = None