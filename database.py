import sqlite3

def connection():
    conn = sqlite3.connect('inventorysystem.db')
    # for accessing the tables
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn