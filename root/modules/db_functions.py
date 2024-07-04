import sqlite3
import bcrypt
import os


db_path = "././instance/users.db"

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
        SELECT courses.cname, courses.description, courses.course_image, courses.cid
        FROM courses
        JOIN course_users ON courses.cid = course_users.cid
        WHERE course_users.uid = ?
    """, (user_id,))
    return c.fetchall()

# --- USER FUNCTIONS --
def create_user(conn, name, email, password, role):
    c = conn.cursor()
    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(password.encode('utf-8'), salt)
    c.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)", (name, email, password, role))
    return c.lastrowid

def delete_user(conn, uid):
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE uid = ?", (uid,))
    return c.rowcount

def find_user_by_email(conn, email):
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    return c.fetchone()

def find_user_by_name(conn, username):
    c = conn.cursor()
    like_username = f"%{username}%"
    c.execute("SELECT * FROM users WHERE name LIKE ?", (like_username,))
    return c.fetchall()

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
    c.execute("DELETE FROM courses WHERE cid = ?", (cid,))
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
def add_task(conn, cid, task_title, task_description, task_content):
    c = conn.cursor()
    # Convert newlines to HTML line breaks
    task_content_formatted = task_content.replace('\n', '<br>')
    c.execute("INSERT INTO course_tasks (cid, task_title, task_description, task_content) VALUES (?, ?, ?, ?)", 
              (cid, task_title, task_description, task_content_formatted))
    return c.lastrowid

def remove_task(conn, cid, tid):
    c = conn.cursor()
    
    # Start a transaction
    c.execute("BEGIN TRANSACTION")
    
    try:
        # Remove the task from course_tasks
        c.execute("DELETE FROM course_tasks WHERE cid = ? AND tid = ?", (cid, tid))
        
        # Remove related entries from completed_tasks
        c.execute("DELETE FROM completed_tasks WHERE course_id = ? AND task_id = ?", (cid, tid))
    
        
        # Commit the transaction if all operations were successful
        conn.commit()
        
        print(f"Task {tid} removed from course {cid} and related tables")
        return c.rowcount  # Returns the number of rows affected in the course_tasks table
    
    except sqlite3.Error as e:
        # If any error occurs, roll back the changes
        conn.rollback()
        print(f"An error occurred: {e}")
        return 0  # Indicate that no rows were affected due to error

def get_tasks(conn, cid):
    c = conn.cursor()
    c.execute("SELECT tid, task_title, task_description FROM course_tasks WHERE cid = ?", (cid,))
    return c.fetchall()

def find_course(conn, cname):
    c = conn.cursor()
    like_pattern = f"%{cname}%"
    c.execute("SELECT cname, description, course_image, cid FROM courses WHERE cname LIKE ?", (like_pattern,))
    return c.fetchall()

def get_task(conn, tid):
    c = conn.cursor()
    c.execute("SELECT tid, task_title, task_description, task_content FROM course_tasks WHERE tid = ?", (tid,))
    return c.fetchone()

def is_task_completed(conn, user_id, course_id, task_id):
    c = conn.cursor()
    c.execute("""
    SELECT COUNT(*) FROM completed_tasks
    WHERE user_id = ? AND course_id = ? AND task_id = ?
    """, (user_id, course_id, task_id))
    return c.fetchone()[0] > 0

def request_author(conn, uid, email, reason, area):
    c = conn.cursor()
    c.execute("INSERT INTO author_requests (uid, email, reason, area) VALUES (?, ?, ?, ?)", (uid, email, reason, area))
    return c.fetchall()

def change_role(conn, uid, new_role):
    c = conn.cursor()
    c.execute("UPDATE users SET role = ? WHERE uid = ?", (new_role, uid))
    return c.rowcount

def change_username(conn, uid, new_username):
    c = conn.cursor()
    c.execute("UPDATE users SET name = ? WHERE uid = ?", (new_username, uid))
    return c.rowcount

def change_email(conn, uid, new_email):
    c = conn.cursor()
    c.execute("UPDATE users SET email = ? WHERE uid = ?", (new_email, uid))
    return c.rowcount

def change_password(conn, uid, new_password):
    c = conn.cursor()
    new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    c.execute("UPDATE users SET password = ? WHERE uid = ?", (new_password, uid))
    return c.rowcount

def delete_account(conn, uid):
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE uid = ?", (uid,))
    return c.rowcount

def mark_task_as_complete(conn, user_id, course_id, task_id):
    c = conn.cursor()
    c.execute('''
    INSERT INTO completed_tasks (user_id, course_id, task_id)
    VALUES (?, ?, ?)
    ''', (user_id, course_id, task_id))
    conn.commit()

def get_user_name(conn, user_id):
    c = conn.cursor()
    c.execute("SELECT name FROM users WHERE uid = ?", (user_id,))
    result = c.fetchone()
    return result[0] if result else "Unknown"

def get_completed_tasks(conn, user_id, course_id):
    c = conn.cursor()
    c.execute('''
    SELECT task_id FROM completed_tasks
    WHERE user_id = ? AND course_id = ?
    ''', (user_id, course_id))
    return [row[0] for row in c.fetchall()]

def calculate_completion_rate(conn, user_id, course_id):
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM course_tasks WHERE cid = ?', (course_id,))
    total_tasks = c.fetchone()[0]
    
    c.execute('''
    SELECT COUNT(*) FROM completed_tasks
    WHERE user_id = ? AND course_id = ?
    ''', (user_id, course_id))
    completed_tasks = c.fetchone()[0]
    
    if total_tasks == 0:
        return 0
    return (completed_tasks / total_tasks) * 100

# --- DEFAULT ACCOUNTS ---

def default_admin(conn):
    c = conn.cursor()
    c.execute("UPDATE users SET role = 'Admin' WHERE email = 'admin@domain.com'")
    return c.rowcount

def default_author(conn):
    c = conn.cursor()
    c.execute("UPDATE users SET role = 'Author' WHERE email = 'author@domain.com'")
    return c.rowcount

def check_admin(conn, uid):
    c = conn.cursor()
    c.execute("SELECT Role FROM users WHERE uid = ?", (uid,))
    if c.fetchone() == 'Admin':
        return True
    else:
        return False

# --- DATABASE CREATION FUNCTION ---
def create():
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
        create_table(connection, "users", ["uid INTEGER PRIMARY KEY AUTOINCREMENT", "name TEXT NOT NULL", "email TEXT UNIQUE", "password TEXT NOT NULL", "role TEXT DEFAULT 'User'"])
        # -- COURSES -- (CREATE COURSES & COURSE_USERS TABLES)
        create_table(connection, "courses", ["cid INTEGER PRIMARY KEY AUTOINCREMENT", "cname TEXT", "description TEXT", "course_image BLOB", "uid INTEGER REFERENCES users(uid)"])
        create_table(connection, "course_users", ["cid INTEGER REFERENCES courses(cid)", "uid INTEGER REFERENCES users(uid)", "CUID INTEGER PRIMARY KEY AUTOINCREMENT"])
        create_table(connection, "course_tasks", ["tid INTEGER PRIMARY KEY AUTOINCREMENT", "cid INTEGER REFERENCES courses(cid)", "task_title TEXT", "task_description TEXT", "task_content TEXT", "completed INTEGER"])
        create_table(connection, "author_requests", ["uid INTEGER REFERENCES users(uid), email TEXT REFERENCES users(email), reason TEXT, area TEXT"])
        create_table(connection, "completed_tasks", ["id INTEGER PRIMARY KEY AUTOINCREMENT", "user_id INTEGER REFERENCES users(uid)", "course_id INTEGER REFERENCES courses(cid)", "task_id INTEGER REFERENCES course_tasks(tid)", "completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"])
        # -- FINISH --
        print("Database + tables created successfully.")
        connection.close()