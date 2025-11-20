"""
ユーザー管理機能

ユーザー情報の管理処理を行う。
"""

from flask import Blueprint, render_template
from flask_login import login_required

user_management_bp = Blueprint("user_management", __name__, url_prefix="/user-management")


@user_management_bp.route("/")
@login_required
def dashboard():
    """
    ユーザー管理のダッシュボードを表示する

    Returns:
        ユーザー管理ダッシュボードのHTML
    """
    return render_template("user_management/dashboard.html")
