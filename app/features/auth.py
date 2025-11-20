"""
認証機能

ユーザーのログイン・ログアウトを処理する。
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.models import User
from app.forms.auth import LoginForm, RegisterForm, ResetPasswordForm

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


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    新規登録画面を表示し、新規登録処理を実行する

    Returns:
        登録成功時: ログイン画面へのリダイレクト
        登録失敗時: 新規登録画面の再表示
    """
    form = RegisterForm()

    if form.validate_on_submit():
        try:
            # ユーザーを作成
            user = User(
                username=form.username.data,
                email=form.email.data,
                department=form.department.data,
                hashed_password=generate_password_hash(form.password.data),
            )

            db.session.add(user)
            db.session.commit()

            flash("アカウントの登録が完了しました。ログインしてください。", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash(f"アカウントの登録中にエラーが発生しました: {e}", "error")

    return render_template("auth/register.html", form=form)


@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    """
    パスワードリセット画面を表示し、パスワード再設定処理を実行する

    Returns:
        再設定成功時: ログイン画面へのリダイレクト
        再設定失敗時: パスワードリセット画面の再表示
    """
    form = ResetPasswordForm()

    if form.validate_on_submit():
        # ユーザー名とメールアドレスでユーザーを検索
        user = User.query.filter_by(username=form.username.data, email=form.email.data).first()

        if user:
            try:
                # パスワードを更新
                user.hashed_password = generate_password_hash(form.new_password.data)
                db.session.commit()

                flash("パスワードの再設定が完了しました。新しいパスワードでログインしてください。", "success")
                return redirect(url_for("auth.login"))
            except Exception as e:
                db.session.rollback()
                flash(f"パスワードの再設定中にエラーが発生しました: {e}", "error")
        else:
            flash("ユーザー名とメールアドレスの組み合わせが正しくありません。", "error")

    return render_template("auth/reset_password.html", form=form)


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
