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
    1. 振興センター（管理権限あり）
       ユーザー名: shinko
       パスワード: shinko123
       メールアドレス: shinko@example.com
       所属: 振興センター
       ユーザー管理権限: あり

    2. 振興センター（管理権限なし）
       ユーザー名: shinko_normal
       パスワード: shinko_normal123
       メールアドレス: shinko_normal@example.com
       所属: 振興センター
       ユーザー管理権限: なし

    3. 染め物屋高橋（管理権限あり）
       ユーザー名: someya
       パスワード: someya123
       メールアドレス: someya@example.com
       所属: 染め物屋高橋
       ユーザー管理権限: あり

    4. 染め物屋高橋（管理権限なし）
       ユーザー名: someya_normal
       パスワード: someya_normal123
       メールアドレス: someya_normal@example.com
       所属: 染め物屋高橋
       ユーザー管理権限: なし
    """
    app = create_app()

    with app.app_context():
        # 既存のテストユーザーをチェック
        shinko_exists = User.query.filter_by(username="shinko").first()
        someya_exists = User.query.filter_by(username="someya").first()
        shinko_normal_exists = User.query.filter_by(username="shinko_normal").first()
        someya_normal_exists = User.query.filter_by(username="someya_normal").first()

        if shinko_exists or someya_exists or shinko_normal_exists or someya_normal_exists:
            print("既存のテストユーザーが見つかりました。")
            print("既存のテストユーザーを削除して新規作成します。")
            if shinko_exists:
                db.session.delete(shinko_exists)
            if someya_exists:
                db.session.delete(someya_exists)
            if shinko_normal_exists:
                db.session.delete(shinko_normal_exists)
            if someya_normal_exists:
                db.session.delete(someya_normal_exists)
            db.session.commit()
            print("既存のテストユーザーを削除しました。")

        # 振興センターのユーザーを作成（ユーザー管理権限あり）
        shinko_user = User(
            username="shinko",
            email="shinko@example.com",
            department="振興センター",
            hashed_password=generate_password_hash("shinko123"),
            can_manage_users=True,
        )

        # 染め物屋高橋のユーザーを作成（ユーザー管理権限あり）
        someya_user = User(
            username="someya",
            email="someya@example.com",
            department="染め物屋高橋",
            hashed_password=generate_password_hash("someya123"),
            can_manage_users=True,
        )

        # 振興センターの通常ユーザーを作成（ユーザー管理権限なし）
        shinko_normal_user = User(
            username="shinko_normal",
            email="shinko_normal@example.com",
            department="振興センター",
            hashed_password=generate_password_hash("shinko_normal123"),
            can_manage_users=False,
        )

        # 染め物屋高橋の通常ユーザーを作成（ユーザー管理権限なし）
        someya_normal_user = User(
            username="someya_normal",
            email="someya_normal@example.com",
            department="染め物屋高橋",
            hashed_password=generate_password_hash("someya_normal123"),
            can_manage_users=False,
        )

        try:
            db.session.add(shinko_user)
            db.session.add(someya_user)
            db.session.add(shinko_normal_user)
            db.session.add(someya_normal_user)
            db.session.commit()

            print("=" * 60)
            print("動作確認用の仮ユーザーを作成しました。")
            print("=" * 60)
            print("\n【振興センター - 管理権限あり】")
            print("  ユーザー名: shinko")
            print("  パスワード: shinko123")
            print("  メールアドレス: shinko@example.com")
            print("  所属: 振興センター")
            print("  ユーザー管理権限: あり")
            print("\n【振興センター - 管理権限なし】")
            print("  ユーザー名: shinko_normal")
            print("  パスワード: shinko_normal123")
            print("  メールアドレス: shinko_normal@example.com")
            print("  所属: 振興センター")
            print("  ユーザー管理権限: なし")
            print("\n【染め物屋高橋 - 管理権限あり】")
            print("  ユーザー名: someya")
            print("  パスワード: someya123")
            print("  メールアドレス: someya@example.com")
            print("  所属: 染め物屋高橋")
            print("  ユーザー管理権限: あり")
            print("\n【染め物屋高橋 - 管理権限なし】")
            print("  ユーザー名: someya_normal")
            print("  パスワード: someya_normal123")
            print("  メールアドレス: someya_normal@example.com")
            print("  所属: 染め物屋高橋")
            print("  ユーザー管理権限: なし")
            print("\n" + "=" * 60)
            print("注意: 本番環境では必ずパスワードを変更してください。")
            print("=" * 60)

        except Exception as e:
            db.session.rollback()
            print(f"エラーが発生しました: {e}")
            sys.exit(1)


if __name__ == "__main__":
    create_test_users()
