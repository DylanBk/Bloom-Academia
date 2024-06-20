import sqlite3

def connect(db_path):
    return sqlite3.connect(db_path)

def create_table(conn, table_name, columns):
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS {} ({})".format(table_name, ", ".join(columns)))
    conn.commit()

def print_table(conn, table_name):
    c = conn.cursor()
    c.execute("SELECT * FROM {}".format(table_name))
    for row in c.fetchall():
        print(row)
    conn.commit()
