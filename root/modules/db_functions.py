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


# --- PROFILE FUNCTIONS ---

def get_user_profile(conn, user_id):
    c = conn.cursor()
    c.execute("SELECT name, email, role FROM users WHERE uid = ?", (user_id,))
    return c.fetchone()

def get_user_courses(conn, user_id):
    c = conn.cursor()
    c.execute("""
        SELECT courses.cname, courses.description
        FROM courses
        JOIN course_users ON courses.cid = course_users.cid
        WHERE course_users.uid = ?
    """, (user_id,))
    return c.fetchall()

# --- USER FUNCTIONS --

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

def join_course(conn, cid, user_id):
    c = conn.cursor()
    c.execute("INSERT INTO course_users (cid, uid) VALUES (?, ?)", (cid, user_id))
    return c.rowcount

def leave_course(conn, cid, user_id):
    c = conn.cursor()
    c.execute("DELETE FROM course_users WHERE cid = ? AND uid = ?", (cid, user_id))
    return c.rowcount

# --- COURSE FUNCTIONS ---
def upload_course(conn, course_title, course_description, course_image, uid):
    c = conn.cursor()
    c.execute("INSERT INTO courses (cname, description, course_image, uid) VALUES (?, ?, ?, ?)", (course_title, course_description, course_image, uid))
    return c.lastrowid

def delete_course(conn, cid):
    c = conn.cursor()
    c.execute("DELETE FROM courses WHERE cid = ?", (cid))
    return c.rowcount

def get_courses(conn):
    c = conn.cursor()
    c.execute("SELECT cname, description, course_image, cid FROM courses")
    return c.fetchall()

def get_course(conn, cid):
    c = conn.cursor()
    c.execute("SELECT cname, description, course_image, cid, uid FROM courses WHERE cid = ?", (cid,))
    return c.fetchone()

# --- TASK FUNCTIONS ---
def add_task(conn, cid, task_title, task_description):
    c = conn.cursor()
    c.execute("INSERT INTO course_tasks (cid, task_title, task_description) VALUES (?, ?, ?)", (cid, task_title, task_description))
    return c.lastrowid

def remove_task(conn, cid, tid):
    c = conn.cursor()
    c.execute("DELETE FROM course_tasks WHERE cid = ? AND tid = ?", (cid, tid))
    return c.rowcount

def get_tasks(conn, cid):
    c = conn.cursor()
    c.execute("SELECT tid, task_title, task_description FROM course_tasks WHERE cid = ?", (cid,))
    return c.fetchall()

def find_course(conn, cname):
    c = conn.cursor()
    c.execute("SELECT cname, description, course_image, cid FROM courses WHERE cname = ?", (cname,))
    return c.fetchall()

def change_role(conn, user_id, new_role):
    c = conn.cursor()
    c.execute("UPDATE users SET role = ? WHERE uid = ?", (new_role, user_id))
    return c.rowcount

def check_admin(conn, user_id):
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE uid = ?", (user_id,))
    if c.fetchone()[0] == 3:
        return True
    else:
        return False

# --- DATABASE CREATION FUNCTION ---
def create():
    db_path = "./instance/users.db"
    db = db_exists(db_path)
    if db:
        print("Database already exists.")
    else:
        print("Creating database...")
        # -- CONNECTION -- (CONNECT TO DATABASE)
        connection = connect(db_path)
        print("checkpoint")
        # -- PRAGMA -- (ENABLE FOREIGN KEYS)
        connection.execute("PRAGMA foreign_keys = ON;") 

        # -- USERS -- (CREATE USERS TABLE)
        create_table(connection, "users", ["uid INTEGER PRIMARY KEY AUTOINCREMENT", "name TEXT NOT NULL", "email TEXT UNIQUE", "password TEXT NOT NULL", "role INTEGER"])
        # -- COURSES -- (CREATE COURSES & COURSE_USERS TABLES)
        create_table(connection, "courses", ["cid INTEGER PRIMARY KEY AUTOINCREMENT", "cname TEXT", "description TEXT", "course_image BLOB", "uid INTEGER REFERENCES users(uid)"])
        create_table(connection, "course_users", ["cid INTEGER REFERENCES courses(cid)", "uid INTEGER REFERENCES users(uid)", "CUID INTEGER PRIMARY KEY AUTOINCREMENT"])
        create_table(connection, "course_tasks", ["tid INTEGER PRIMARY KEY AUTOINCREMENT", "cid INTEGER REFERENCES courses(cid)", "task_title TEXT", "task_description TEXT", "completed INTEGER"])
        create_table(connection, "users_tasks", ["tid INTEGER REFERENCES course_tasks(tid)", "uid INTEGER REFERENCES users(uid)", "TUID INTEGER PRIMARY KEY AUTOINCREMENT"])
        
        # -- FINISH --
        print("Database + tables created successfully.")
        connection.close()