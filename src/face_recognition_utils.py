# src/face_recognition_utils.py

import face_recognition
import numpy as np
from io import BytesIO
import base64

def decode_image(image_data):
    # image_dataが_bytesIOオブジェクトかどうかをチェック
    if isinstance(image_data, BytesIO):
        # 既に_bytesIOオブジェクトであればそのまま返す
        return image_data
    else:
        # Base64でエンコードされた画像データをデコードし、BytesIOオブジェクトを返す
        # ここで、image_dataが文字列として渡されることを期待しています
        image_data = base64.b64decode(image_data.split(",")[1])
        return BytesIO(image_data)

def get_face_encodings(image_data):
    # decode_image関数を使用して画像データをデコード
    image = decode_image(image_data)
    # face_recognitionを使用して画像を読み込み
    loaded_image = face_recognition.load_image_file(image)
    # 画像から顔のエンコーディングを取得
    face_encodings = face_recognition.face_encodings(loaded_image)
    return face_encodings
