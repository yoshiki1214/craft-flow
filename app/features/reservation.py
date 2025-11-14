"""
予約管理機能

予約情報の管理処理を行う。
"""

from flask import Blueprint, render_template

reservation_bp = Blueprint("reservation", __name__, url_prefix="/reservation")


@reservation_bp.route("/")
def index():
    """
    予約管理のトップページ

    Returns:
        トップページのHTML
    """
    return render_template("reservation/index.html")
