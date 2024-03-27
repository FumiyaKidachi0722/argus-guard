# src/views/authenticate.py

from flask import Blueprint, request, jsonify
import sqlite3
import face_recognition
import numpy as np
from src.face_recognition_utils import decode_image, get_face_encodings
from database import DATABASE


authenticate_blueprint = Blueprint('authenticate', __name__)

@authenticate_blueprint.route("/authenticate", methods=["POST"])
def authenticate():
    data = request.get_json()
    image_data = decode_image(data["image"])
    face_encodings = get_face_encodings(image_data)

    if face_encodings:
        face_encoding = face_encodings[0]
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute("SELECT name, face_encoding FROM faces")
            known_faces = c.fetchall()

        known_face_encodings = [np.frombuffer(face[1], dtype=np.float64) for face in known_faces]
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.4)

        if True in matches:
            first_match_index = matches.index(True)
            name = known_faces[first_match_index][0]
            return jsonify({"message": f"認証成功: {name}"})
        else:
            return jsonify({"message": "認証失敗"}), 401
    else:
        return jsonify({"message": "顔が検出されませんでした。"}), 400
