# 顔認証システム

このドキュメントでは、顔認証システムの構築手順を説明します。以下のステップに従ってください。

## 目次

- [顔認証システム](#顔認証システム)
  - [目次](#目次)
  - [1. 環境設定](#1-環境設定)
    - [仮想環境の設定](#仮想環境の設定)
    - [仮想環境のアクティベーション](#仮想環境のアクティベーション)
    - [必要なライブラリのインストール](#必要なライブラリのインストール)
  - [2. データベースの準備](#2-データベースの準備)
    - [動作確認](#動作確認)
  - [3. 顔検出機能の実装](#3-顔検出機能の実装)
    - [動作確認](#動作確認-1)
  - [4. Web カメラからの映像取得と顔認識](#4-web-カメラからの映像取得と顔認識)
  - [5. データベースとの顔照合](#5-データベースとの顔照合)
  - [6. ディレクトリ構造](#6-ディレクトリ構造)
    - [補足](#補足)

## 1. 環境設定

### 仮想環境の設定

プロジェクトフォルダ内で以下のコマンドを実行し、仮想環境を作成します。

```bash
python -m venv venv
```

### 仮想環境のアクティベーション

仮想環境をアクティブにします。

```bash
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows
```

### 必要なライブラリのインストール

`requirements.txt`ファイルを作成し、以下の内容を追加します。

```
opencv-python
face_recognition
numpy
```

次に、以下のコマンドで必要なライブラリをインストールします。

```bash
pip install -r requirements.txt
```

## 2. データベースの準備

データベースの準備は、システムが顔の特徴を格納する場所を提供します。SQLite を例に説明しますが、必要に応じて他のデータベースシステムに置き換えても構いません。

```python
# database_setup.py
import sqlite3

# データベース接続（存在しない場合は新規作成）
conn = sqlite3.connect('face_database.db')
c = conn.cursor()

# テーブルの作成（既に存在する場合はスキップ）
c.execute('''
CREATE TABLE IF NOT EXISTS faces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    face_encoding BLOB NOT NULL
)
''')
conn.commit()
conn.close()
```

### 動作確認

以下のコマンドでデータベース設定スクリプトを実行し、`face_database.db` ファイルがプロジェクトディレクトリ内に作成されることを確認します。

```bash
python3 src/database_setup.py
```

## 3. 顔検出機能の実装

顔検出機能は、画像やビデオストリームから顔を特定し、その特徴を抽出するプロセスです。この機能は`face_recognition`ライブラリを使用して実装されます。

システムが認識する顔のデータをデータベースに追加します。まず、顔の特徴を抽出してデータベースに保存する必要があります。

```python
# src/add_face_to_database.py

import sqlite3
import face_recognition

# データベースに接続
conn = sqlite3.connect('face_database.db')
c = conn.cursor()

# データを挿入するためのSQLクエリ
insert_query = "INSERT INTO faces (name, face_encoding) VALUES (?, ?)"

# 自分の写真から顔の特徴を抽出するための画像ファイルパス
# image_path = "./images/FumiyaKidachi.jpg"  # あなたの写真のファイルパスに置き換えてください
image_path = "./images/FumiyaKidachi.png"  # あなたの写真のファイルパスに置き換えてください
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
```

### 動作確認

顔データの登録を確認するために、`src/add_face_to_database.py`を実行します。

```bash
python3 src/add_face_to_database.py
```

## 4. Web カメラからの映像取得と顔認識

リアルタイムで映像を取得し、映像内の顔を認識するために、Web カメラを使用します。顔検出と認識のコードを`src/face_recognition_live.py`に追加します。

```python
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
    conn = sqlite3.connect('face_database.db')
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
    matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.4)
    name = "Unknown"

    # 一致が見られる場合、もっとも近い顔を特定
    if True in matches:
        # 一致した顔の距離を計算
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
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

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            name = recognize_face(face_encoding, known_face_encodings, known_face_names)

            # 顔周辺にボックスを描画
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # 名前のラベルをボックスの下に描画
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

        # フレームを画面に表示
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_and_recognize()
```

## 5. データベースとの顔照合

検出された顔をデータベースに保存されている顔データと照合し、個人を識別します。これにより、システムは既知の個人を認識できるようになります。

## 6. ディレクトリ構造

プロジェクトのディレクトリ構造を整理し、コード管理を容易にします。

```
顔認証システム/
├── face_database.db
├── requirements.txt
├── venv/
└── src/
    ├── __init__.py
    ├── add_face_to_database.py
    ├── database_setup.py
    ├── face_recognition_live.py
    └── main.py
```

### 補足

- このシステムは顔認証の基本的な枠組みを提供します。セキュリティ強化、エラーハンドリングの改善、パフォーマンスの最適化など、さらに開発が必要です。
- プロジェクトの要件に応じて、データベースに顔データを追加する方法や、新しい顔データの追加方法を調整してください。
- `face_recognition` ライブラリは dlib の顔認識モデルを背景に使用し、比較的高い精度を提供しますが、照明条件や顔の角度など
