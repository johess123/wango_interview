from typing import Annotated

from pydantic import BaseModel
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm , OAuth2PasswordBearer 

# oauth2_token_scheme = Depends(OAuth2PasswordBearer(tokenUrl="users/login"))
# login_form_schema = Depends(OAuth2PasswordRequestForm)
oauth2_token_scheme = Annotated[str,Depends(OAuth2PasswordBearer(tokenUrl="users/login"))]
login_form_schema = Annotated[OAuth2PasswordRequestForm, Depends()]

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str