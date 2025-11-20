"""
動作確認用の仮ユーザーを作成するスクリプト

振興センターと染め物屋高橋の2つのユーザーを作成します。
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app, db  # noqa: E402
from app.models import User  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402


def create_test_users():
    """
    動作確認用の仮ユーザーを作成する

    作成されるユーザー:
    1. 振興センター
       ユーザー名: shinko
       パスワード: shinko123
       メールアドレス: shinko@example.com
       所属: 振興センター

    2. 染め物屋高橋
       ユーザー名: someya
       パスワード: someya123
       メールアドレス: someya@example.com
       所属: 染め物屋高橋
    """
    app = create_app()

    with app.app_context():
        # 既存のテストユーザーをチェック
        shinko_exists = User.query.filter_by(username="shinko").first()
        someya_exists = User.query.filter_by(username="someya").first()

        if shinko_exists or someya_exists:
            print("既存のテストユーザーが見つかりました。")
            print("既存のテストユーザーを削除して新規作成します。")
            if shinko_exists:
                db.session.delete(shinko_exists)
            if someya_exists:
                db.session.delete(someya_exists)
            db.session.commit()
            print("既存のテストユーザーを削除しました。")

        # 振興センターのユーザーを作成
        shinko_user = User(
            username="shinko",
            email="shinko@example.com",
            department="振興センター",
            hashed_password=generate_password_hash("shinko123"),
        )

        # 染め物屋高橋のユーザーを作成
        someya_user = User(
            username="someya",
            email="someya@example.com",
            department="染め物屋高橋",
            hashed_password=generate_password_hash("someya123"),
        )

        try:
            db.session.add(shinko_user)
            db.session.add(someya_user)
            db.session.commit()

            print("=" * 60)
            print("動作確認用の仮ユーザーを作成しました。")
            print("=" * 60)
            print("\n【振興センター】")
            print("  ユーザー名: shinko")
            print("  パスワード: shinko123")
            print("  メールアドレス: shinko@example.com")
            print("  所属: 振興センター")
            print("\n【染め物屋高橋】")
            print("  ユーザー名: someya")
            print("  パスワード: someya123")
            print("  メールアドレス: someya@example.com")
            print("  所属: 染め物屋高橋")
            print("\n" + "=" * 60)
            print("注意: 本番環境では必ずパスワードを変更してください。")
            print("=" * 60)

        except Exception as e:
            db.session.rollback()
            print(f"エラーが発生しました: {e}")
            sys.exit(1)


if __name__ == "__main__":
    create_test_users()
