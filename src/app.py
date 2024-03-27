# src/app.py

from flask import Flask
from database import init_db
from views.index import index_blueprint
from views.register import register_blueprint
from views.authenticate import authenticate_blueprint

def create_app():
    app = Flask(__name__, template_folder='../templates') # テンプレートフォルダのパスをここで指定
    init_db()
    app.register_blueprint(index_blueprint)
    app.register_blueprint(register_blueprint)
    app.register_blueprint(authenticate_blueprint)
    return app

if __name__ == "__main__":
    app = create_app()  # create_app 関数から Flask アプリケーションインスタンスを取得
    app.run(debug=True)  # 取得したインスタンスを実行
