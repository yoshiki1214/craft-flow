"""
精算書ファイル作成機能

精算書ファイルの作成処理を行う。
"""

from flask import Blueprint, render_template
from flask_login import login_required
from app.utils.decorators import shinko_center_required

settlement_bp = Blueprint("settlement", __name__, url_prefix="/settlement")


@settlement_bp.route("/")
@login_required
@shinko_center_required
def index():
    """
    精算書ファイル作成のトップページ

    Returns:
        トップページのHTML
    """
    return render_template("settlement/index.html")
