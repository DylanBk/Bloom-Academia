import sqlite3
import bcrypt
import os

# --- CONNECTION ---
def connect(db_path):
    return sqlite3.connect(db_path)

# --- TABLES ---
def create_table(conn, table_name, columns):
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS {} ({})".format(table_name, ", ".join(columns)))
    conn.commit()

# --- CHECKS ---
def db_exists(db_path):
    if not os.path.exists(db_path):
        return False
    else:
        return True

# --- PRINT ---
def print_database(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM sqlite_master WHERE type='table'")
    for row in c:
        print(row[0])
    conn.close()

# --- USER FUNCTIONS ---
def create_user(conn, name, email, password, role):
    c = conn.cursor()
    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    c.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)", (name, email, password, role))
    return c.lastrowid

def delete_user(conn, email):
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE email = ?", (email,))
    return c.rowcount

def find_user(conn, email):
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    return c.fetchone()

def change_password(conn, email, new_password):
    c = conn.cursor()
    new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    c.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
    return c.rowcount

def change_email(conn, email, new_email):
    c = conn.cursor()
    c.execute("UPDATE users SET email = ? WHERE email = ?", (new_email, email))
    return c.rowcount

def change_name(conn, new_name, email):
    c = conn.cursor()
    c.execute("UPDATE users SET name = ? WHERE email = ?", (new_name, email))
    return c.rowcount

# --- USER DATABASE CREATION FUNCTION ---
def create():
    db_path = "root/instance/users.db"
    db = db_exists(db_path)
    if db:
        print("Database already exists.")
    else:
        print("Creating database...")
        # -- CONNECTION -- (CONNECT TO DATABASE)
        connection = connect(db_path)

        # -- PRAGMA -- (ENABLE FOREIGN KEYS)
        connection.execute("PRAGMA foreign_keys = ON;") 

        # -- USERS -- (CREATE USERS TABLE)
        create_table(connection, "users", ["uid INTEGER PRIMARY KEY AUTOINCREMENT", "name TEXT NOT NULL", "email TEXT UNIQUE", "password TEXT NOT NULL", "role INTEGER"])
        # -- COURSES -- (CREATE COURSES & COURSE_USERS TABLES)
        create_table(connection, "courses", ["cid INTEGER PRIMARY KEY AUTOINCREMENT", "cname TEXT", "description TEXT", "course_image TEXT"])
        create_table(connection, "course_users", ["cid INTEGER REFERENCES courses(cid)", "uid INTEGER REFERENCES users(uid)", "CUID INTEGER PRIMARY KEY AUTOINCREMENT"])

        # -- FINISH --
        print("Databases created successfully.")
        connection.close()