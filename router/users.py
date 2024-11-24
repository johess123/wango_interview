from fastapi import APIRouter, HTTPException, status, Depends, Header, Query
import models.users as UserModel # users model
import models.images as ImageModel # images model
import models.jwt as JWTModel # jwt model
from schemas.users import User as UserSchema # users schema
from schemas.change_password import Password as PasswordSchema # password schema
from auth.passwd import verify_password, get_password_hash # verify, encrypt password
from schemas.auth import login_form_schema, oauth2_token_scheme , Token # auth schema
from auth.jwt import create_token_pair, verify_user # jwt
from typing import Optional

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

# 驗證帳密
def authenticate_user(name: str, password: str):
    # 使用者存在
    record = UserModel.get_user_by_name(name)
    if len(record) == 0:
        return False
    # 密碼正確
    hashed_password = record[0]["password"]
    if not verify_password(password, hashed_password):
        return False
    return record

# 驗證 token
async def verify_user_dependency(access_token: oauth2_token_scheme,refresh_token: Optional[str] = Header(None, alias="refresh-token")):
    return await verify_user(access_token, refresh_token)

# Admin function
@router.get("/", summary="取得所有使用者資料", response_description="所有使用者資料")
def get_users():
    users = UserModel.get_all_users()
    return {"data": users}

# 註冊
@router.post("/register", summary="註冊帳號", response_description="註冊結果", status_code=status.HTTP_201_CREATED)
async def regist_user(user: UserSchema):
    """
    註冊帳號
    - body
        - **username**: 使用者名稱
        - **password**: 密碼
    - 回傳資料
        
    """
    record = UserModel.get_user_by_name(user.username)
    if len(record) != 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
            detail=f"User name {user.username} is already registered",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user.password = get_password_hash(user.password)
    UserModel.regist_user(user.username, user.password)
    return {"status": "success"}

# 登入
@router.post("/login", summary="登入帳號", response_description="登入 token", response_model=Token)
async def login_user(form_data: login_form_schema):
    """
    登入帳號
    - body
        - **username**: 使用者名稱
        - **password**: 密碼
    - 回傳資料

    """
    # 驗證帳密
    record = authenticate_user(form_data.username, form_data.password)
    if record == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = record[0]["id"]
    # 產生 token
    token_pair = await create_token_pair({"user_id": user_id, "username": form_data.username},{"user_id": user_id, "username": form_data.username})
    return token_pair.dict()

# 登出
@router.post("/logout/{user_id}", summary="登出帳號", response_description="登出結果")
def logout_user(user_id: int, token_data: dict = Depends(verify_user_dependency)):
    """
    登出帳號
    - path
        - **user_id**: 使用者 id
    - header
        - **Authorization**: bearer type access token
        - **refresh-token**: refresh token
    - 回傳資料
    """
    # 註銷 token
    return {"status": "success"}

# 顯示個人資料
@router.get("/me", summary="取得個人資料", response_description="個人資料")
async def get_user(token_data: dict = Depends(verify_user_dependency)):
    """
    顯示個人資料
    - header
        - **Authorization**: bearer type access token
        - **refresh-token**: refresh token
    - 回傳資料
    """
    # 從 token 取得 user name
    user_name = token_data["payload"]["username"]
    # 回傳 name, 作品數
    user_data = UserModel.get_user_data(user_name)
    response_data = {"data": user_data}
    if token_data["new_access_token"]:
        response_data["new_access_token"] = token_data["new_access_token"]
    return response_data

# 修改密碼
@router.put("/users/password", summary="修改密碼", response_description="修改結果")
def update_password(user: PasswordSchema, token_data: dict = Depends(verify_user_dependency)):
    """
    修改密碼
    - header
        - **Authorization**: bearer type access token
        - **refresh-token**: refresh token
    - body
        - **original_password**: 原密碼
        - **new_password**: 新密碼
    - 回傳資料
    """
    # 從 token 取得 user name
    user_name = token_data["payload"]["username"]
    # 取得原密碼
    record = UserModel.get_user_by_name(user_name)
    hashed_password = record[0]["password"]
    # 修改密碼
    if not verify_password(user.original_password, hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    UserModel.update_password(user_name, user.new_password)
    response_data = {"status": "success"}
    if token_data["new_access_token"]:
        response_data["new_access_token"] = token_data["new_access_token"]
    return response_data

# 刪除自己帳號
@router.delete("/{user_id}", summary="刪除帳號", response_description="刪除結果")
def delete_user(user_id: int, token_data: dict = Depends(verify_user_dependency)):
    """
    刪除帳號
    - path
        - **user_id**: 使用者 id
    - header
        - **Authorization**: bearer type access token
        - **refresh-token**: refresh token
    - 回傳資料
    """
    # 確認 id 所有者與 token
    if user_id != token_data["payload"]["user_id"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not the owner of this user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 刪除 user
    UserModel.delete_user(user_id)
    # 註銷 token
    # FIXME
    return {"status": "success"}

# 查看使用者的所有照片
@router.get("/{user_id}/images", summary="取得使用者所有照片", response_description="使用者所有照片資料")
def get_user_all_image(user_id: int, token_data: dict = Depends(verify_user_dependency), limit: int = Query(10, ge=1, le=50), offset: int = Query(0, ge=0)):
    """
    取得使用者的所有照片
    - path
        - **user_id**: 使用者 id
    - query
        - **limit**: 顯示筆數
        - **offset**: 從第幾筆開始
    - header
        - **Authorization**: bearer type access token
        - **refresh-token**: refresh token
    - 回傳資料
    """
    # 確認使用者存在
    user = UserModel.get_image_by_id(user_id)
    if len(user) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail="Can not find this ID's user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 取出使用者所有照片
    user_all_image = ImageModel.get_user_all_image(user_id, limit, offset)
    response_data = {"data": user_all_image}
    if token_data["new_access_token"]:
        response_data["new_access_token"] = token_data["new_access_token"]
    return response_data

# 查看使用者的某照片
@router.get("/{user_id}/images/{image_id}", summary="取得使用者該照片", response_description="使用者該照片資料")
def get_user_image(user_id: int, image_id: int, token_data: dict = Depends(verify_user_dependency)):
    """
    取得使用者該照片
    - path
        - **user_id**: 使用者 id
        - **image_id**: 照片 id
    - header
        - **Authorization**: bearer type access token
        - **refresh-token**: refresh token
    - 回傳資料
    """
    # 確認使用者存在
    user = UserModel.get_image_by_id(user_id)
    if len(user) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail="Can not find this ID's user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 取出使用者該照片
    user_image = ImageModel.get_user_image(user_id, image_id)
    # 確認使用者該照片存在
    if len(user_image) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail="Can not find this ID's image of the user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    response_data = {"data": user_image}
    if token_data["new_access_token"]:
        response_data["new_access_token"] = token_data["new_access_token"]
    return response_data