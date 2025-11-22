"""Fix alembic_version table to match current migration files"""

import sqlite3
from pathlib import Path

# データベースパス
db_path = Path("instance/app.db")

if not db_path.exists():
    print(f"データベースファイルが見つかりません: {db_path}")
    exit(1)

# データベースに接続
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# 現在の状態を確認
cursor.execute("SELECT * FROM alembic_version")
current_version = cursor.fetchone()
print(f"現在のバージョン: {current_version[0] if current_version else 'None'}")

# 98e888f0e5afが記録されている場合、c4ecfbb93930に更新
if current_version and current_version[0] == "98e888f0e5af":
    cursor.execute("UPDATE alembic_version SET version_num = 'c4ecfbb93930'")
    conn.commit()
    print("バージョンを c4ecfbb93930 に更新しました")

    # 確認
    cursor.execute("SELECT * FROM alembic_version")
    updated_version = cursor.fetchone()
    print(f"更新後のバージョン: {updated_version[0]}")
else:
    print(f"現在のバージョンは {current_version[0] if current_version else 'None'} です。")

conn.close()
