from dbConfig import conn, cur

def add_to_blacklist(token: str):
    sql = "insert into jwt_blacklist (token) values (%s);"
    cur.execute(sql,(token,))
    conn.commit()

def check_blacklist(token: str):
    sql = "select * from jwt_blacklist where token=%s;"
    cur.execute(sql,(token,))
    return cur.fetchall()