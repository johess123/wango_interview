import mysql.connector

from dotenv import load_dotenv
import os
from pathlib import Path

# 載入 .env
BASE_DIR = Path(__file__)
ENV_PATH = BASE_DIR / "setting" / ".env"
load_dotenv(dotenv_path=ENV_PATH)

try:
    conn = mysql.connector.connect(
        user = os.getenv("MYSQL_USER")
        password = os.getenv("MYSQL_PASSWORD")
        host = os.getenv("MYSQL_HOST")
        port = int(os.getenv("MYSQL_PORT"))
        database = os.getenv("MYSQL_DATABASE")
    )
except:
    print("Error connecting to DB")
    exit(1)

cur=conn.cursor(dictionary=True)