from dbConfig import conn, cur
from fastapi import UploadFile

def get_all_images(limit: int, offset: int):
    sql = "select * from image limit %s,%s;"
    cur.execute(sql,(offset, limit))
    return cur.fetchall()

def get_user_all_image(user_id: int, limit: int, offset: int):
    sql = "select * from image where user_id=%s limit %s,%s;"
    cur.execute(sql,(user_id, offset, limit))
    return cur.fetchall()

def get_user_image(user_id: int, image_id: int):
    sql = "select * from image where user_id=%s and id=%s;"
    cur.execute(sql,(user_id, image_id))
    return cur.fetchall()

def get_image_by_id(image_id: int):
    sql = "select * from image where id=%s;"
    cur.execute(sql,(image_id,))
    return cur.fetchall()

def upload_image(file_name: str, file_path: str, text: str, user_id: int):
    sql = "insert into image (file_name, file_path, text, user_id) values (%s,%s,%s,%s);"
    cur.execute(sql,(file_name, file_path, text, user_id))
    conn.commit()
    return cur.lastrowid

def update_image(file_name: str, file_path: str, text: str, image_id: int):
    print(file_name, file_path, text, image_id)
    sql = "update image set file_name=%s, file_path=%s, text=%s where id=%s;"
    cur.execute(sql,(file_name, file_path, text, image_id))
    conn.commit()

def delete_image(image_id: int):
    sql = "delete from image where id=%s;"
    cur.execute(sql,(image_id,))
    conn.commit()