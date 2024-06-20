import sqlite3
import bcrypt

def connect(db_path):
    return sqlite3.connect(db_path)

def create_table(conn, table_name, columns):
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS {} ({})".format(table_name, ", ".join(columns)))
    conn.commit()

def print_database(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM sqlite_master WHERE type='table'")
    for row in c:
        print(row[0])
    conn.close()

def create_user(conn, name, email, password):
    c = conn.cursor()
    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))

def delete_user(conn, email):
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE email = ?", (email,))

def get_user(conn, email):  # returns uid
    c = conn.cursor()
    c.execute("SELECT uid FROM users WHERE email = ?", (email,))
    return c.fetchone()[0]

def change_password(conn, email, new_password):
    c = conn.cursor()
    new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    c.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
