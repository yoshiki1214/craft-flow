"""
PDFデバッグスクリプト

PDFファイルの構造を確認し、メタデータとテーブルデータの抽出結果を表示します。
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.utils.pdf_processor import (
    extract_metadata_from_pdf,
    extract_table_data_from_pdf,
    parse_sales_data,
)


def debug_pdf(pdf_path: str):
    """
    PDFファイルのデバッグ情報を表示する

    Args:
        pdf_path: PDFファイルのパス
    """
    print("=" * 70)
    print(f"PDFデバッグ: {pdf_path}")
    print("=" * 70)

    # メタデータの抽出
    print("\n[1] メタデータの抽出")
    print("-" * 70)
    metadata = extract_metadata_from_pdf(pdf_path)
    print(f"レジ番号: {metadata.get('pos_number', 'N/A')}")
    print(f"営業日: {metadata.get('sale_date', 'N/A')}")
    print(f"出力日時: {metadata.get('reported_at', 'N/A')}")

    # テーブルデータの抽出
    print("\n[2] テーブルデータの抽出")
    print("-" * 70)
    table_data = extract_table_data_from_pdf(pdf_path)
    print(f"抽出した行数: {len(table_data)}")

    if table_data:
        print("\n最初の5行のテーブルデータ:")
        for i, row in enumerate(table_data[:5]):
            print(f"  行{i+1}: {row}")
        if len(table_data) > 5:
            print(f"  ... (残り{len(table_data)-5}行)")

    # データの整形
    print("\n[3] データの整形")
    print("-" * 70)
    sales_records = parse_sales_data(table_data, metadata)
    print(f"整形後のレコード数: {len(sales_records)}")

    if sales_records:
        print("\n最初の3件のレコード:")
        for i, record in enumerate(sales_records[:3]):
            print(f"  レコード{i+1}:")
            print(f"    商品コード: {record.get('product_code', 'N/A')}")
            print(f"    商品名: {record.get('product_name', 'N/A')}")
            print(f"    数量: {record.get('quantity', 'N/A')}")
            print(f"    単価: {record.get('unit_price', 'N/A')}")
            print(f"    小計: {record.get('subtotal', 'N/A')}")

    print("\n" + "=" * 70)
    print("デバッグ完了")
    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python scripts/debug_pdf.py <PDFファイルのパス>")
        print("例: python scripts/debug_pdf.py C:\\Users\\e-tkh\\Downloads\\POS1.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]
    debug_pdf(pdf_path)
