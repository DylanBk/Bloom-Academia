import sqlite3

def connection():
    conn = sqlite3.connect("main.db")