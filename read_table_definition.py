#!/usr/bin/env python3
"""
テーブル定義書を読み込んで内容を表示するスクリプト
"""
import pandas as pd
import sys
import os

# Excelファイルのパス
excel_file = "settlement-app/テーブル定義書.xlsx"

# ファイルの存在確認
if not os.path.exists(excel_file):
    print(f"エラー: ファイルが見つかりません: {excel_file}")
    sys.exit(1)

try:
    # Excelファイルを読み込む
    xls = pd.ExcelFile(excel_file)

    print("=" * 80)
    print("テーブル定義書の内容")
    print("=" * 80)
    print(f"\nシート一覧: {xls.sheet_names}\n")

    # すべてのシートを読み込む
    for sheet_name in xls.sheet_names:
        print("\n" + "=" * 80)
        print(f"シート名: {sheet_name}")
        print("=" * 80)

        df = pd.read_excel(excel_file, sheet_name=sheet_name)

        # データフレームの情報を表示
        print(f"\n行数: {len(df)}, 列数: {len(df.columns)}")
        print(f"\n列名: {list(df.columns)}")
        print("\nデータ内容:")
        print(df.to_string())
        print("\n")

        # データ型情報も表示
        print("データ型情報:")
        print(df.dtypes)
        print("\n")

except Exception as e:
    print(f"エラーが発生しました: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
