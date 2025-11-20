"""
認証フォーム

ログイン等の認証関連フォームを定義する。
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    """
    ログインフォーム

    ユーザー名とパスワードでログインするためのフォーム。

    Attributes:
        username: ユーザー名
        password: パスワード
        submit: 送信ボタン
    """

    username = StringField(
        "ユーザー名",
        validators=[
            DataRequired(message="ユーザー名を入力してください。"),
            Length(max=255, message="ユーザー名は255文字以内で入力してください。"),
        ],
        render_kw={
            "placeholder": "ユーザー名を入力",
            "class": (
                "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                "focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            ),
        },
    )
    password = PasswordField(
        "パスワード",
        validators=[
            DataRequired(message="パスワードを入力してください。"),
        ],
        render_kw={
            "placeholder": "パスワードを入力",
            "class": (
                "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                "focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            ),
        },
    )
    submit = SubmitField(
        "ログイン",
        render_kw={
            "class": (
                "w-full flex justify-center py-2 px-4 border border-transparent "
                "rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 "
                "hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 "
                "focus:ring-indigo-500"
            ),
        },
    )
