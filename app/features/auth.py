"""
認証機能

ユーザーのログイン・ログアウトを処理する。
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from app.models import User
from app.forms.auth import LoginForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    ログイン画面を表示し、ログイン処理を実行する

    Returns:
        ログイン成功時: ダッシュボードへのリダイレクト
        ログイン失敗時: ログイン画面の再表示
    """
    form = LoginForm()

    if form.validate_on_submit():
        # ユーザー名でユーザーを検索
        user = User.query.filter_by(username=form.username.data).first()

        # ユーザーが存在し、パスワードが正しい場合
        if user and check_password_hash(user.hashed_password, form.password.data):
            login_user(user)
            flash("ログインに成功しました。", "success")
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("main.dashboard"))
        else:
            flash("ユーザー名またはパスワードが正しくありません。", "error")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    """
    ログアウト処理を実行する

    Returns:
        ログイン画面へのリダイレクト
    """
    logout_user()
    flash("ログアウトしました。", "info")
    return redirect(url_for("auth.login"))
