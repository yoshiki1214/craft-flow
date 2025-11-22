"""
メインダッシュボード機能

アプリケーションのメインメニュー画面を提供する。
"""

from flask import Blueprint, render_template
from flask_login import login_required

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def dashboard():
    """
    メインダッシュボード（メニュー画面）を表示する

    Returns:
        メインダッシュボードのHTML
    """
    return render_template("main/dashboard.html")
