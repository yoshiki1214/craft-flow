"""
ユーザー管理機能

ユーザー情報の管理処理を行う。
"""

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from app.models import User
from app.utils.decorators import user_management_required
from app.forms.user_management import EditUserForm

user_management_bp = Blueprint("user_management", __name__, url_prefix="/user-management")


@user_management_bp.route("/")
@login_required
@user_management_required
def dashboard():
    """
    ユーザー管理のダッシュボードを表示する

    ログインユーザーの所属に応じて、同じ所属のユーザーのみを表示する。

    Returns:
        ユーザー管理ダッシュボードのHTML
    """
    # ログインユーザーの所属と同じ所属のユーザーのみを取得（ID番号の昇順で並び替え）
    users = User.query.filter_by(department=current_user.department).order_by(User.id.asc()).all()
    return render_template("user_management/dashboard.html", users=users)


@user_management_bp.route("/edit/<int:user_id>", methods=["GET", "POST"])
@login_required
@user_management_required
def edit_user(user_id):
    """
    ユーザー情報を編集する

    Args:
        user_id: 対象ユーザーのID

    Returns:
        編集成功時: ユーザー管理ダッシュボードへのリダイレクト
        編集失敗時: ユーザー編集画面の再表示
    """
    user = User.query.get_or_404(user_id)

    # 同じ所属のユーザーのみ編集可能
    if user.department != current_user.department:
        flash("このユーザーを編集する権限がありません。", "error")
        return redirect(url_for("user_management.dashboard"))

    form = EditUserForm(obj=user)
    form.original_email = user.email
    form.original_username = user.username

    if form.validate_on_submit():
        try:
            # ユーザー情報を更新
            user.username = form.username.data
            user.email = form.email.data
            user.department = form.department.data

            # パスワードが入力されている場合のみ更新
            if form.password.data:
                user.hashed_password = generate_password_hash(form.password.data)

            db.session.commit()

            flash(f"{user.username}さんの情報を更新しました。", "success")
            return redirect(url_for("user_management.dashboard"))
        except Exception as e:
            db.session.rollback()
            flash(f"ユーザー情報の更新中にエラーが発生しました: {e}", "error")

    return render_template("user_management/edit.html", form=form, user=user)


@user_management_bp.route("/delete/<int:user_id>", methods=["POST"])
@login_required
@user_management_required
def delete_user(user_id):
    """
    ユーザーを削除する

    Args:
        user_id: 対象ユーザーのID

    Returns:
        ユーザー管理ダッシュボードへのリダイレクト
    """
    user = User.query.get_or_404(user_id)

    # 同じ所属のユーザーのみ削除可能
    if user.department != current_user.department:
        flash("このユーザーを削除する権限がありません。", "error")
        return redirect(url_for("user_management.dashboard"))

    # 自分自身は削除できない
    if user.id == current_user.id:
        flash("自分自身を削除することはできません。", "error")
        return redirect(url_for("user_management.dashboard"))

    try:
        username = user.username
        db.session.delete(user)
        db.session.commit()

        flash(f"{username}さんを削除しました。", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"ユーザーの削除中にエラーが発生しました: {e}", "error")

    return redirect(url_for("user_management.dashboard"))


@user_management_bp.route("/toggle-user-management/<int:user_id>", methods=["POST"])
@login_required
@user_management_required
def toggle_user_management(user_id):
    """
    ユーザーの管理権限を切り替える

    Args:
        user_id: 対象ユーザーのID

    Returns:
        ユーザー管理ダッシュボードへのリダイレクト
    """
    user = User.query.get_or_404(user_id)

    # 同じ所属のユーザーのみ権限変更可能
    if user.department != current_user.department:
        flash("このユーザーの権限を変更する権限がありません。", "error")
        return redirect(url_for("user_management.dashboard"))

    # 自分自身の権限は変更できない
    if user.id == current_user.id:
        flash("自分自身の管理権限は変更できません。", "error")
        return redirect(url_for("user_management.dashboard"))

    try:
        user.can_manage_users = not user.can_manage_users
        db.session.commit()

        status = "付与" if user.can_manage_users else "剥奪"
        flash(f"{user.username}さんのユーザー管理権限を{status}しました。", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"権限の変更中にエラーが発生しました: {e}", "error")

    return redirect(url_for("user_management.dashboard"))
