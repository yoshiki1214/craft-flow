"""
正規表現パターンのテストスクリプト

実際のPDFテキストで正規表現が正しく動作するか確認します。
"""

import re
import sys
import io

# Windows環境でのエンコーディング問題を回避
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# 実際のPDFテキスト（pdf_extracted_text.txtから）
test_text = """=== ページ 1 ===
盛岡手づくり村 日次売上レポート
レジ番号：POS1
営業日：令和7年11月5日
出力日時：令和7年11月6日 17時30分
商品コード 商品名 単価 数量 小計 商品コード 商品名 単価 数量 小計"""

print("=" * 70)
print("正規表現パターンのテスト")
print("=" * 70)

# レジ番号のパターン
print("\n[1] レジ番号の抽出")
print("-" * 70)
pos_patterns = [
    r"レジ番号[：:]\s*POS\s*(\d+)",
    r"POS\s*(\d+)",
    r"レジ[：:]\s*(\d+)",
]
for pattern in pos_patterns:
    match = re.search(pattern, test_text, re.IGNORECASE)
    if match:
        print(f"✓ マッチ: {pattern} -> POS{match.group(1)}")
    else:
        print(f"✗ マッチなし: {pattern}")

# 営業日のパターン
print("\n[2] 営業日の抽出")
print("-" * 70)
sale_date_patterns = [
    r"営業日[：:]\s*(令和|平成|昭和)(\d+)年(\d+)月(\d+)日",
    r"営業日[^\d]*(\d+)年(\d+)月(\d+)日",
    r"(令和|平成|昭和)(\d+)年(\d+)月(\d+)日",
]
for pattern in sale_date_patterns:
    match = re.search(pattern, test_text)
    if match:
        print(f"✓ マッチ: {pattern}")
        print(f"  グループ: {match.groups()}")
        print(f"  全体: {match.group(0)}")
    else:
        print(f"✗ マッチなし: {pattern}")

# 出力日時のパターン
print("\n[3] 出力日時の抽出")
print("-" * 70)
reported_patterns = [
    r"出力日時[：:]\s*(令和|平成|昭和)(\d+)年(\d+)月(\d+)日\s*(\d+)時(\d+)分",
    r"出力日時[^\d]*(\d+)年(\d+)月(\d+)日\s*(\d+)時(\d+)分",
    r"出力日[：:]\s*(令和|平成|昭和)(\d+)年(\d+)月(\d+)日\s*(\d+)時(\d+)分",
]
for pattern in reported_patterns:
    match = re.search(pattern, test_text)
    if match:
        print(f"✓ マッチ: {pattern}")
        print(f"  グループ: {match.groups()}")
        print(f"  全体: {match.group(0)}")
    else:
        print(f"✗ マッチなし: {pattern}")

print("\n" + "=" * 70)
