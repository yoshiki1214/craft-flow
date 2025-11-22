"""
インポートチェックスクリプト

必要なパッケージが正しくインストールされているか確認します。
"""

import sys

print("=" * 50)
print("パッケージのインポートチェック")
print("=" * 50)

# チェックするパッケージ
packages = [
    ("flask", "Flask"),
    ("flask_sqlalchemy", "Flask-SQLAlchemy"),
    ("flask_migrate", "Flask-Migrate"),
    ("pdfplumber", "pdfplumber"),
    ("tabula", "tabula-py"),
    ("pandas", "pandas"),
]

errors = []
success = []

for module_name, package_name in packages:
    try:
        __import__(module_name)
        print(f"[OK] {package_name} ({module_name})")
        success.append(package_name)
    except ImportError as e:
        print(f"[ERROR] {package_name} ({module_name}): {e}")
        errors.append((package_name, str(e)))

print("=" * 50)
print(f"成功: {len(success)}/{len(packages)}")
if errors:
    print(f"エラー: {len(errors)}/{len(packages)}")
    print("\nエラーが発生したパッケージをインストールしてください:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
else:
    print("\nすべてのパッケージが正常にインストールされています。")
    print("アプリケーションを起動できます: python app.py")
