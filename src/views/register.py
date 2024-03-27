# src/views/register.py

from flask import Blueprint, request, jsonify
import sqlite3
from src.face_recognition_utils import decode_image, get_face_encodings
from src.database import DATABASE

register_blueprint = Blueprint('register', __name__)

@register_blueprint.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data["name"]
    image_data = decode_image(data["image"])
    face_encodings = get_face_encodings(image_data)

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
