# src/face_recognition_live.py

# pylint: disable=no-member
import cv2
import face_recognition
import numpy as np
import face_recognition

# def load_known_faces():
#     # 既知の人物の顔画像からエンコーディングを生成
#     image_of_person = face_recognition.load_image_file(
#         # "./images/FumiyaKidachi.png"
#         "./images/test01.png"
#         )
#     person_face_encoding = face_recognition.face_encodings(image_of_person)[0]

#     known_face_encodings = [
#         person_face_encoding,
#     ]
#     known_face_names = [
#         "Person's Name",
#     ]
#     return known_face_encodings, known_face_names
import sqlite3
import numpy as np


def load_known_faces():
    conn = sqlite3.connect("face_database.db")
    c = conn.cursor()

    # データベースから顔の名前とエンコーディングを取得
    c.execute("SELECT name, face_encoding FROM faces")
    known_face_encodings = []
    known_face_names = []

    for row in c.fetchall():
        name, face_encoding = row
        # データベースから読み込んだBLOBエンコーディングをnumpy配列に変換
        face_encoding_array = np.frombuffer(face_encoding, dtype=np.float64)
        known_face_encodings.append(face_encoding_array)
        known_face_names.append(name)

    conn.close()
    return known_face_encodings, known_face_names


def recognize_face(face_encoding, known_face_encodings, known_face_names):
    # 既知の顔エンコーディングと比較し、一致するかどうかを確認（より厳格な設定）
    matches = face_recognition.compare_faces(
        known_face_encodings, face_encoding, tolerance=0.4
    )
    name = "Unknown"

    # 一致が見られる場合、もっとも近い顔を特定
    if True in matches:
        # 一致した顔の距離を計算
        face_distances = face_recognition.face_distance(
            known_face_encodings, face_encoding
        )
        # 一致した顔の中で最も距離が短いものを選択
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]

    return name


def capture_and_recognize():
    known_face_encodings, known_face_names = load_known_faces()
    video_capture = cv2.VideoCapture(0)

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(
            face_locations, face_encodings
        ):
            name = recognize_face(face_encoding, known_face_encodings, known_face_names)

            # 顔周辺にボックスを描画
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # 名前のラベルをボックスの下に描画
            cv2.rectangle(
                frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED
            )
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(
                frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1
            )

        # フレームを画面に表示
        cv2.imshow("Video", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    capture_and_recognize()
