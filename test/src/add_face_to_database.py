# src/add_face_to_database.py

import sqlite3
import face_recognition

# データベースに接続
conn = sqlite3.connect("face_database.db")
c = conn.cursor()

# データを挿入するためのSQLクエリ
insert_query = "INSERT INTO faces (name, face_encoding) VALUES (?, ?)"

# 自分の写真から顔の特徴を抽出するための画像ファイルパス
# image_path = "./images/FumiyaKidachi.jpg"  # あなたの写真のファイルパスに置き換えてください
image_path = (
    "./images/FumiyaKidachi.png"  # あなたの写真のファイルパスに置き換えてください
)
# image_path = "./images/test01.png"  # あなたの写真のファイルパスに置き換えてください

# 自分の写真から顔の特徴を抽出
image = face_recognition.load_image_file(image_path)
face_encodings = face_recognition.face_encodings(image)

if face_encodings:
    # データベースに顔の特徴を保存
    name = "Fumiya Kidachi"  # あなたの名前
    # name = "test01"  # あなたの名前
    c.execute(insert_query, (name, face_encodings[0].tobytes()))
    conn.commit()
    print("Your face data has been added to the database.")
else:
    print("No face detected in the image.")

# データベース接続を閉じる
conn.close()
