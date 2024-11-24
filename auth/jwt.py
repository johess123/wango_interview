# 產生 jwt, 驗證 jwt
from fastapi import HTTPException, status, Header
from datetime import datetime, timedelta
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from schemas.auth import oauth2_token_scheme, Token
from typing import Optional

from dotenv import load_dotenv
import os
from pathlib import Path

# 載入 .env
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / "setting" / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# SECRET_KEY = "kenny"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 1
# REFRESH_TOKEN_EXPIRE_MINUTES = 5
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))

# create access token
async def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt

# create refresh token
async def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt

# create token pair (access_token, refresh_token)
async def create_token_pair(access_data: dict,refresh_data:dict) -> Token:
    access_token = await create_access_token(access_data)
    refresh_token = await create_refresh_token(refresh_data)
    print("access_token:",access_token)
    print("refresh_token:",refresh_token)
    return Token(access_token=access_token,refresh_token=refresh_token,token_type="bearer")

# verify token (access_token, refresh_token)
async def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        return {
            "status": "valid",
            "payload": payload,
            "message": "Token is valid"
        }
    except ExpiredSignatureError:
        return {
            "status": "expired",
            "payload": None,
            "message": "Expired token"
        }
    except JWTError:
        return {
            "status": "invalid",
            "payload": None,
            "message": "Invalid token"
        }

# verify user
async def verify_user(access_token: oauth2_token_scheme,refresh_token: Optional[str] = Header(None,alias="refresh-token")):
    # 驗證 access token
    access_token_result = await verify_token(access_token)
    if access_token_result["status"] == "invalid":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=access_token_result["message"]
        )
    if access_token_result["status"] == "expired":
        # 檢查 refresh token
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token expired, refresh token required",
            )
        # 驗證 refresh token
        refresh_token_result = await verify_token(refresh_token)
        if refresh_token_result["status"] != "valid":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=refresh_token_result["message"]
            )
        # 產生新 access token
        new_access_token = await create_access_token({"username": refresh_token_result["payload"]["username"]})
        return {
            "payload": refresh_token_result["payload"],
            "new_access_token": new_access_token,
        }
    return {
        "payload": access_token_result["payload"],
        "new_access_token": None,
    }