"""Check constraints in daily_sales table"""

import sqlite3
from pathlib import Path

db_path = Path("instance/app.db")
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# daily_salesテーブルの定義を確認
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='daily_sales'")
result = cursor.fetchone()
if result:
    print("daily_sales table definition:")
    print(result[0])
    print()

# インデックスと制約を確認
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='daily_sales'")
indexes = cursor.fetchall()
print("Indexes on daily_sales:")
for idx in indexes:
    print(f"  {idx[0]}: {idx[1]}")

conn.close()
