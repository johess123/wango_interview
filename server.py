from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from router import users, images
from pathlib import Path as FilePath

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