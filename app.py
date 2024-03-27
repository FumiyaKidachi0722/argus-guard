from flask import Flask, render_template, request, jsonify
import sqlite3
import face_recognition
import numpy as np
from io import BytesIO
import base64

app = Flask(__name__)

# データベース設定
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


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data["name"]
    image = data["image"]
    image_data = base64.b64decode(image.split(",")[1])
    image_array = face_recognition.load_image_file(BytesIO(image_data))
    face_encodings = face_recognition.face_encodings(image_array)

    if face_encodings:
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO faces (name, face_encoding) VALUES (?, ?)",
                (name, face_encodings[0].tobytes()),
            )
            conn.commit()
        return jsonify({"message": f"{name}が登録されました。"})
    else:
        return jsonify({"message": "顔が検出されませんでした。"}), 400


@app.route("/authenticate", methods=["POST"])
def authenticate():
    data = request.get_json()
    image = data["image"]
    image_data = base64.b64decode(image.split(",")[1])
    image_array = face_recognition.load_image_file(BytesIO(image_data))
    face_encodings = face_recognition.face_encodings(image_array)

    if face_encodings:
        face_encoding = face_encodings[0]
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute("SELECT name, face_encoding FROM faces")
            known_faces = c.fetchall()

        known_face_encodings = [
            np.frombuffer(face[1], dtype=np.float64) for face in known_faces
        ]
        matches = face_recognition.compare_faces(
            known_face_encodings, face_encoding, tolerance=0.4
        )

        if True in matches:
            first_match_index = matches.index(True)
            name = known_faces[first_match_index][0]
            return jsonify({"message": f"認証成功: {name}"})
        else:
            return jsonify({"message": "認証失敗"}), 401
    else:
        return jsonify({"message": "顔が検出されませんでした。"}), 400


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
