"""
デコレータユーティリティ

認証・認可に関するデコレータを提供する。
"""

from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def shinko_center_required(f):
    """
    振興センターのユーザーのみアクセス可能にするデコレータ

    振興センター以外のユーザーがアクセスした場合、403エラーを返す。

    Args:
        f: デコレートする関数

    Returns:
        デコレートされた関数
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("ログインが必要です。", "error")
            return redirect(url_for("auth.login"))
        if current_user.department != "振興センター":
            flash("この機能にアクセスする権限がありません。", "error")
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def user_management_required(f):
    """
    ユーザー管理権限を持つユーザーのみアクセス可能にするデコレータ

    ユーザー管理権限を持たないユーザーがアクセスした場合、403エラーを返す。

    Args:
        f: デコレートする関数

    Returns:
        デコレートされた関数
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("ログインが必要です。", "error")
            return redirect(url_for("auth.login"))
        if not current_user.can_manage_users:
            flash("ユーザー管理機能にアクセスする権限がありません。", "error")
            abort(403)
        return f(*args, **kwargs)

    return decorated_function
