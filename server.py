from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from router import users, images
from pathlib import Path as FilePath

'''
1. api 設計、產出文件
    - api tag, summary, description, response description
    - status code
2. 後端驗證參數，只接收符合型態的資料 (Validation Rule)
3. 資料庫操作限制, ex: 一次 select 筆數限制
4. Unit Test
5. user 權限驗證 (JWT)
6. route 分檔
'''

app = FastAPI()
app.include_router(users.router)
app.include_router(images.router)

# 靜態資源路徑
static_path = FilePath(__file__).parent / "static" / "images"
static_path.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {"Hello": "FastAPI"}