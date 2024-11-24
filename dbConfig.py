import mysql.connector

try:
    conn = mysql.connector.connect(
        user="kenny",
        password="Kenny061256",
        host="127.0.0.1",
        port=3306,
        database="recognition"
    )
except:
    print("Error connecting to DB")
    exit(1)

cur=conn.cursor(dictionary=True)