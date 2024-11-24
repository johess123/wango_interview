from dbConfig import conn, cur
from bcrypt import hashpw, gensalt, checkpw

def get_all_users():
    sql = "select * from user;"
    cur.execute(sql,())
    return cur.fetchall()

def get_user_by_id(id: int):
    sql = "select * from user where id=%s;"
    cur.execute(sql,(id,))
    return cur.fetchall()

def get_user_by_name(name: str):
    sql = "select * from user where name=%s;"
    cur.execute(sql,(name,))
    return cur.fetchall()

def get_user_data(name: str):
    sql = "select user.id,user.name, count(image.id) as image_count from user left join image on image.user_id=user.id where user.name=%s group by user.id;"
    cur.execute(sql,(name,))
    return cur.fetchall()

def regist_user(name: str, password: str):
    sql = "insert into user (name, password) values (%s, %s);"
    cur.execute(sql,(name, password))
    conn.commit()

def update_password(name: str, new_password: str):
    hashed_password = hashpw(new_password.encode('utf-8'), gensalt()).decode('utf-8')
    sql = "update user set password=%s where name=%s;"
    cur.execute(sql,(hashed_password, name))
    conn.commit()

def delete_user(user_id: int):
    sql = "delete from user where id=%s;"
    cur.execute(sql,(user_id,))
    conn.commit()