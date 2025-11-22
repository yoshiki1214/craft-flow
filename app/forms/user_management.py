"""
ユーザー管理フォーム

ユーザー情報の編集に使用するフォームを定義する。
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Optional, Regexp, ValidationError
from app.models import User


class EditUserForm(FlaskForm):
    """
    ユーザー編集フォーム

    ユーザー情報を編集するためのフォーム。

    Attributes:
        username: ユーザー名
        email: メールアドレス
        department: 所属
        password: パスワード（任意、変更する場合のみ入力）
        submit: 送信ボタン
    """

    username = StringField(
        "ユーザー名",
        validators=[
            DataRequired(message="ユーザー名を入力してください。"),
            Length(min=1, max=255, message="ユーザー名は1文字以上255文字以下で入力してください。"),
        ],
        render_kw={
            "placeholder": "ユーザー名を入力",
            "class": (
                "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                "focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm py-2.5 px-3"
            ),
        },
    )
    email = StringField(
        "メールアドレス",
        validators=[
            DataRequired(message="メールアドレスを入力してください。"),
            Email(message="有効なメールアドレスを入力してください。例: user@example.com"),
            Length(max=255, message="メールアドレスは255文字以下で入力してください。"),
        ],
        render_kw={
            "placeholder": "example@email.com",
            "type": "email",
            "class": (
                "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                "focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm py-2.5 px-3"
            ),
        },
    )
    department = SelectField(
        "所属",
        choices=[
            ("振興センター", "振興センター"),
            ("染め物屋高橋", "染め物屋高橋"),
        ],
        validators=[
            DataRequired(message="所属を選択してください。"),
        ],
        render_kw={
            "class": (
                "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                "focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm py-2.5 px-3"
            ),
        },
    )
    password = PasswordField(
        "パスワード（変更する場合のみ入力）",
        validators=[
            Optional(),
            Length(min=8, message="パスワードは8文字以上で入力してください。"),
            Regexp(
                r"^(?=.*[0-9])(?=.*[a-zA-Z])[a-zA-Z0-9]{8,}$",
                message="パスワードは英数字を組み合わせた8文字以上で入力してください。",
            ),
        ],
        render_kw={
            "placeholder": "パスワードを変更する場合のみ入力",
            "class": (
                "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                "focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm py-2.5 px-3"
            ),
        },
    )
    submit = SubmitField(
        "更新",
        render_kw={
            "class": (
                "w-full flex justify-center py-2 px-4 border border-transparent "
                "rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 "
                "hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 "
                "focus:ring-indigo-500"
            ),
        },
    )

    def __init__(self, *args, **kwargs):
        """フォームを初期化する"""
        super().__init__(*args, **kwargs)
        self.original_email = None
        self.original_username = None

    def validate_email(self, field):
        """
        メールアドレスの重複をチェックする

        Args:
            field: メールアドレスフィールド

        Raises:
            ValidationError: メールアドレスが既に使用されている場合
        """
        if self.original_email and field.data == self.original_email:
            return

        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError("このメールアドレスは既に使用されています。")

    def validate_username(self, field):
        """
        ユーザー名の重複をチェックする

        Args:
            field: ユーザー名フィールド

        Raises:
            ValidationError: ユーザー名が既に使用されている場合
        """
        if self.original_username and field.data == self.original_username:
            return

        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError("このユーザー名は既に使用されています。")
