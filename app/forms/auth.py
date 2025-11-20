"""
認証フォーム

ログイン等の認証関連フォームを定義する。
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from app.models import User


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
            Length(min=3, max=255, message="ユーザー名は3文字以上で入力してください。"),
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


class RegisterForm(FlaskForm):
    """
    新規登録フォーム

    ユーザー新規登録のためのフォーム。

    Attributes:
        username: ユーザー名
        email: メールアドレス
        password: パスワード
        password_confirm: パスワード確認
        department: 所属
        submit: 送信ボタン
    """

    username = StringField(
        "ユーザー名",
        validators=[
            DataRequired(message="ユーザー名を入力してください。"),
            Length(min=3, max=255, message="ユーザー名は3文字以上で入力してください。"),
        ],
        render_kw={
            "placeholder": "ユーザー名を入力",
            "class": (
                "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                "focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            ),
        },
    )
    email = EmailField(
        "メールアドレス",
        validators=[
            DataRequired(message="メールアドレスを入力してください。"),
            Email(message="有効なメールアドレスを入力してください。"),
            Length(max=255, message="メールアドレスは255文字以内で入力してください。"),
        ],
        render_kw={
            "placeholder": "メールアドレスを入力",
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
            Length(min=8, message="パスワードは8文字以上で入力してください。"),
            Regexp(
                r"^(?=.*[0-9])(?=.*[a-zA-Z])[a-zA-Z0-9]{8,}$",
                message="パスワードは英数字を組み合わせた8文字以上で入力してください。",
            ),
        ],
        render_kw={
            "placeholder": "パスワードを入力",
            "class": (
                "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                "focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            ),
        },
    )
    password_confirm = PasswordField(
        "パスワード（確認）",
        validators=[
            DataRequired(message="パスワード（確認）を入力してください。"),
            EqualTo("password", message="パスワードが一致しません。"),
        ],
        render_kw={
            "placeholder": "パスワードを再入力",
            "class": (
                "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                "focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            ),
        },
    )
    department = SelectField(
        "所属",
        choices=[
            ("", "選んでください"),
            ("振興センター", "振興センター"),
            ("染め物屋高橋", "染め物屋高橋"),
        ],
        validators=[
            DataRequired(message="所属を選択してください。"),
        ],
        render_kw={
            "class": (
                "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                "focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            ),
        },
    )
    submit = SubmitField(
        "登録",
        render_kw={
            "class": (
                "w-full flex justify-center py-2 px-4 border border-transparent "
                "rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 "
                "hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 "
                "focus:ring-indigo-500"
            ),
        },
    )

    def validate_username(self, username):
        """ユーザー名の重複チェック"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("このユーザー名は既に使用されています。")

    def validate_email(self, email):
        """メールアドレスの重複チェック"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("このメールアドレスは既に使用されています。")


class ResetPasswordForm(FlaskForm):
    """
    パスワードリセットフォーム

    パスワードを再設定するためのフォーム。

    Attributes:
        username: ユーザー名
        email: メールアドレス
        new_password: 新しいパスワード
        new_password_confirm: 新しいパスワード（確認）
        submit: 送信ボタン
    """

    username = StringField(
        "ユーザー名",
        validators=[
            DataRequired(message="ユーザー名を入力してください。"),
        ],
        render_kw={
            "placeholder": "ユーザー名を入力",
            "class": (
                "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                "focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            ),
        },
    )
    email = EmailField(
        "メールアドレス",
        validators=[
            DataRequired(message="メールアドレスを入力してください。"),
            Email(message="有効なメールアドレスを入力してください。例: user@example.com"),
        ],
        render_kw={
            "placeholder": "example@email.com",
            "type": "email",
            "class": (
                "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                "focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            ),
        },
    )
    new_password = PasswordField(
        "新しいパスワード",
        validators=[
            DataRequired(message="新しいパスワードを入力してください。"),
            Length(min=8, message="パスワードは8文字以上で入力してください。"),
            Regexp(
                r"^(?=.*[0-9])(?=.*[a-zA-Z])[a-zA-Z0-9]{8,}$",
                message="パスワードは英数字を組み合わせた8文字以上で入力してください。",
            ),
        ],
        render_kw={
            "placeholder": "新しいパスワードを入力",
            "class": (
                "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                "focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            ),
        },
    )
    new_password_confirm = PasswordField(
        "新しいパスワード（確認）",
        validators=[
            DataRequired(message="新しいパスワード（確認）を入力してください。"),
            EqualTo("new_password", message="パスワードが一致しません。"),
        ],
        render_kw={
            "placeholder": "新しいパスワードを再入力",
            "class": (
                "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
                "focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            ),
        },
    )
    submit = SubmitField(
        "パスワードを再設定",
        render_kw={
            "class": (
                "w-full flex justify-center py-2 px-4 border border-transparent "
                "rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 "
                "hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 "
                "focus:ring-indigo-500"
            ),
        },
    )

    def validate_email(self, field):
        """
        メールアドレスとユーザー名の組み合わせを検証する

        Args:
            field: メールアドレスフィールド

        Raises:
            ValidationError: ユーザー名とメールアドレスの組み合わせが正しくない場合
        """
        # ユーザー名とメールアドレスの両方が入力されている場合のみ検証
        if self.username.data and field.data:
            user = User.query.filter_by(username=self.username.data, email=field.data).first()
            if not user:
                raise ValidationError("ユーザー名とメールアドレスの組み合わせが正しくありません。")
