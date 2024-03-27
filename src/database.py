# src/database.py

import sqlite3

DATABASE = "face_database.db"

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS faces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                face_encoding BLOB NOT NULL
            )
            """
        )
        conn.commit()
