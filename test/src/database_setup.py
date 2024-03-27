# src/database_setup.py

import sqlite3

# データベース接続（存在しない場合は新規作成）
conn = sqlite3.connect("face_database.db")
c = conn.cursor()

# テーブルの作成（既に存在する場合はスキップ）
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
conn.close()
