# src/views/index.py

from flask import Blueprint, render_template

# Blueprintの定義
index_blueprint = Blueprint('index', __name__)

@index_blueprint.route("/")
def index():
    # index.htmlテンプレートをレンダリングして返す
    return render_template("index.html")
