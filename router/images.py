from fastapi import APIRouter, Path, HTTPException, status, Depends, Header, Request, Response, File, UploadFile, Query
import models.users as UserModel # users model
import models.images as ImageModel # images model
from schemas.auth import oauth2_token_scheme , Token # auth schema
from schemas.images import ImageListResponse as ImageListResponseSchema # image list response schema
from auth.jwt import create_access_token, verify_user # jwt
from typing import Optional
import shutil
from uuid import uuid4
import os
import easyocr

router = APIRouter(
    prefix="/images",
    tags=["images"],
)

# easyocr model
reader = easyocr.Reader(['en'])

# 驗證 token
async def verify_user_dependency(access_token: oauth2_token_scheme,refresh_token: Optional[str] = Header(None, alias="refresh-token")):
    return await verify_user(access_token, refresh_token)

# 查看所有照片
@router.get("/", summary="取得所有照片", response_description="所有照片資料", response_model=ImageListResponseSchema)
async def get_all_images(request: Request, response: Response, token_data: dict = Depends(verify_user_dependency),limit: int = Query(10, ge=1, le=50), offset: int = Query(0, ge=0)):
    """
    取得所有照片
    - query
        - **limit**: 顯示筆數
        - **offset**: 從第幾筆開始
    - header
        - **Authorization**: bearer type access token
        - **refresh-token**: refresh token
    - 回傳資料
        - **id**: 照片 id
        - **file_name**: 檔案名稱
        - **file_path**: 檔案路徑
        - **text**: 辨識文字
        - **user_id**: 擁有者 id
    """
    all_images = ImageModel.get_all_images(limit, offset)
    response_data = {"data": all_images}
    if token_data["new_access_token"]:
        response_data["new_access_token"] = token_data["new_access_token"]
    return response_data

# 上傳照片
@router.post("/", summary="上傳照片", response_description="照片資料", status_code=status.HTTP_201_CREATED, response_model=ImageListResponseSchema)
async def upload_image(file: UploadFile = File(...), token_data: dict = Depends(verify_user_dependency)):
    """
    上傳照片
    - header
        - **Authorization**: bearer type access token
        - **refresh-token**: refresh token
    - body
        - **file**: 照片檔案
    - 回傳資料
        - **file_name**: 檔案名稱
        - **file_path**: 檔案路徑
        - **text**: 辨識文字
        - **user_id**: 擁有者 id
    """
    # 驗證檔案類型
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Only JPEG and PNG are allowed.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 儲存圖片
    image_uuid = str(uuid4())
    file_name = image_uuid+"_"+file.filename
    file_path = "static/images/"+file_name
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # 辨識
    result = reader.readtext(file_path)
    all_text = ""
    for (bbox, text, prob) in result:
        all_text = all_text + text + " "
    # 從 token 取得 user name, user_id
    user_id = token_data["payload"]["user_id"]
    # 存 db
    image_id = ImageModel.upload_image(file_name, file_path, all_text, user_id)
    response_data = {"data":[{"id": image_id, "file_name": file.filename, "file_path": file_path, "text": all_text, "user_id": user_id}]}
    if token_data["new_access_token"]:
        response_data["new_access_token"] = token_data["new_access_token"]
    return response_data

# 更新照片
@router.put("/{image_id}", summary="更新照片", response_description="照片資料", response_model=ImageListResponseSchema)
async def update_image(image_id: int = Path(...,title="照片id",description="照片的流水編號",), file: UploadFile = File(...), token_data: dict = Depends(verify_user_dependency)):
    """
    更新照片
    - path
        - **image_id**: 照片 id
    - header
        - **Authorization**: bearer type access token
        - **refresh-token**: refresh token
    - body
        - **file**: 照片檔案
    - 回傳資料
        - **id**: 照片 id
        - **file_name**: 檔案名稱
        - **file_path**: 檔案路徑
        - **text**: 辨識文字
        - **user_id**: 擁有者 id
    """
    # 確認 id 所有者與 token
    original_image = ImageModel.get_image_by_id(image_id)
    user_id = original_image[0]["user_id"]
    if user_id != token_data["payload"]["user_id"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not the owner of this user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 驗證檔案類型
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Only JPEG and PNG are allowed.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 取得照片路徑並刪除
    orginal_file_path = original_image[0]["file_path"]
    os.remove(orginal_file_path)
    # 儲存照片
    image_uuid = str(uuid4())
    file_name = image_uuid+"_"+file.filename
    file_path = "static/images/"+file_name
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # 辨識
    result = reader.readtext(file_path)
    all_text = ""
    for (bbox, text, prob) in result:
        all_text = all_text + text + " "
    # 存 db
    ImageModel.update_image(file_name, file_path, all_text, image_id)
    response_data = {"data":[{"id": image_id, "file_name": file.filename, "file_path": file_path, "text": all_text, "user_id": user_id}]}
    if token_data["new_access_token"]:
        response_data["new_access_token"] = token_data["new_access_token"]
    return response_data

# 刪除照片
@router.delete("/{image_id}", summary="刪除照片", response_description="執行結果")
def delete_image(image_id: int = Path(...,title="照片id",description="照片的流水編號",), token_data: dict = Depends(verify_user_dependency)):
    """
    刪除照片
    - path
        - **image_id**: 照片 id
    - header
        - **Authorization**: bearer type access token
        - **refresh-token**: refresh token
    - 回傳資料
        - **status**: 刪除結果
    """
    # 確認 id 所有者與 token
    original_image = ImageModel.get_image_by_id(image_id)
    user_id = original_image[0]["user_id"]
    if user_id != token_data["payload"]["user_id"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not the owner of this user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 取得照片路徑並刪除
    orginal_file_path = original_image[0]["file_path"]
    os.remove(orginal_file_path)
    # 刪除照片
    ImageModel.delete_image(image_id)
    return {"status": "success"}