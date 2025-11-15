"""
Userモデルの動作確認スクリプト

Userモデルが正しくインポートでき、テーブルが作成されているか確認する。
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app, db  # noqa: E402
from app.models import User  # noqa: E402


def test_user_model():
    """Userモデルの動作確認"""
    app = create_app()

    with app.app_context():
        # テーブルが存在するか確認
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()

        print("=" * 50)
        print("Userモデルの動作確認")
        print("=" * 50)

        # テーブル存在確認
        if "users" in tables:
            print("✓ usersテーブルが存在します")

            # カラム情報を取得
            columns = inspector.get_columns("users")
            print(f"\nカラム数: {len(columns)}")
            print("\nカラム一覧:")
            for col in columns:
                print(f"  - {col['name']}: {col['type']} (nullable={col['nullable']})")

            # インデックス情報を取得
            indexes = inspector.get_indexes("users")
            if indexes:
                print("\nインデックス一覧:")
                for idx in indexes:
                    print(f"  - {idx['name']}: {idx['column_names']} (unique={idx['unique']})")
            else:
                print("\nインデックス: なし（emailの一意制約は別途確認）")

            # ユニーク制約を確認
            unique_constraints = inspector.get_unique_constraints("users")
            if unique_constraints:
                print("\nユニーク制約:")
                for uc in unique_constraints:
                    print(f"  - {uc['name']}: {uc['column_names']}")
        else:
            print("✗ usersテーブルが存在しません")
            print("  マイグレーションを実行してください: flask db upgrade")
            return False

        # モデルクラスの動作確認
        print("\n" + "=" * 50)
        print("モデルクラスの動作確認")
        print("=" * 50)

        try:
            # モデルが正しくインポートできているか確認
            print(f"✓ Userモデルクラス: {User}")
            print(f"✓ テーブル名: {User.__tablename__}")
            print(f"✓ カラム数: {len(User.__table__.columns)}")

            # カラム名の確認
            column_names = [col.name for col in User.__table__.columns]
            expected_columns = ["id", "username", "email", "department", "hashed_password", "created_at"]

            print(f"\n期待されるカラム: {expected_columns}")
            print(f"実際のカラム: {column_names}")

            if set(column_names) == set(expected_columns):
                print("✓ すべてのカラムが正しく定義されています")
            else:
                print("✗ カラムの不一致があります")
                return False

            print("\n✓ すべての確認が完了しました")
            return True

        except Exception as e:
            print(f"✗ エラーが発生しました: {e}")
            import traceback

            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = test_user_model()
    sys.exit(0 if success else 1)
