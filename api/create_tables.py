# https://www.geeksforgeeks.org/sql/sql-cheat-sheet/


import sqlite3

conn = sqlite3.connect("chat.db")
cursor = conn.cursor()
# Users Table
# Copilot helped identify an error where i made the username primary key
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               username TEXT UNIQUE NOT NULL,
               password TEXT NOT NULL)                
""")

# Messages Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS messages(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               message TEXT NOT NULL,
               user_origin INTEGER NOT NULL,
               user_destination INTEGER NOT NULL,
               is_deleted INTEGER NOT NULL DEFAULT 0,
               created_at INTEGER NOT NULL,
               updated_at INTEGER NOT NULL,

               FOREIGN KEY (user_origin) REFERENCES users(id),
               FOREIGN KEY (user_destination) REFERENCES users(id)
                
               )                
""")
conn.commit()
