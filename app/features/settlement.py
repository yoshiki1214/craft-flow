"""
精算書ファイル作成機能

精算書ファイルの作成処理を行う。
"""

from flask import Blueprint, render_template

settlement_bp = Blueprint("settlement", __name__, url_prefix="/settlement")


@settlement_bp.route("/")
def index():
    """
    精算書ファイル作成のトップページ

    Returns:
        トップページのHTML
    """
    return render_template("settlement/index.html")
