"""
正規表現パターンの直接テスト

実際のPDFテキストファイルを使用してテストします。
"""

import re
import sys
import io

# Windows環境でのエンコーディング問題を回避
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# 実際のPDFテキストを読み込む
with open("pdf_extracted_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

print("=" * 70)
print("正規表現パターンの直接テスト")
print("=" * 70)

# 営業日のパターン
print("\n[1] 営業日の抽出テスト")
print("-" * 70)
sale_patterns = [
    r"営業[^\d]*(令和|平成|昭和)(\d+)[年月](\d+)[年月](\d+)日",  # 特殊文字対応
    r"営業[^\d]*(\d+)[年月](\d+)[年月](\d+)日",  # 特殊文字対応（数字のみ）
    r"営業[^\d]*(令和|平成|昭和)(\d+)年(\d+)月(\d+)日",
    r"営業日[：:]\s*(令和|平成|昭和)(\d+)年(\d+)月(\d+)日",
    r"営業[^\d]*(\d+)年(\d+)月(\d+)日",
]

for pattern in sale_patterns:
    match = re.search(pattern, text)
    if match:
        print(f"✓ マッチ: {pattern}")
        print(f"  グループ数: {len(match.groups())}")
        print(f"  グループ: {match.groups()}")
        print(f"  全体: {repr(match.group(0))}")
    else:
        print(f"✗ マッチなし: {pattern}")

# 出力日時のパターン
print("\n[2] 出力日時の抽出テスト")
print("-" * 70)
reported_patterns = [
    r"出力[^\d]*(令和|平成|昭和)(\d+)[年月](\d+)[年月](\d+)日[^\d]*(\d+)時(\d+)分",  # 特殊文字対応
    r"出力[^\d]*(\d+)[年月](\d+)[年月](\d+)日[^\d]*(\d+)時(\d+)分",  # 特殊文字対応（数字のみ）
    r"出力[^\d]*(令和|平成|昭和)(\d+)年(\d+)月(\d+)日[^\d]*(\d+)時(\d+)分",
    r"出力日時[：:]\s*(令和|平成|昭和)(\d+)年(\d+)月(\d+)日\s*(\d+)時(\d+)分",
    r"出力[^\d]*(\d+)年(\d+)月(\d+)日[^\d]*(\d+)時(\d+)分",
]

for pattern in reported_patterns:
    match = re.search(pattern, text)
    if match:
        print(f"✓ マッチ: {pattern}")
        print(f"  グループ数: {len(match.groups())}")
        print(f"  グループ: {match.groups()}")
        print(f"  全体: {repr(match.group(0))}")
    else:
        print(f"✗ マッチなし: {pattern}")

# テキストの該当部分を表示
print("\n[3] テキストの該当部分")
print("-" * 70)
lines = text.split("\n")
for i, line in enumerate(lines[:10]):
    if "営業" in line or "出力" in line:
        print(f"行{i+1}: {repr(line)}")

print("\n" + "=" * 70)
