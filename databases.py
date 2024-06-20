import sqlite3

def connection() -> None:
    conn = sqlite3.connect("main.db")