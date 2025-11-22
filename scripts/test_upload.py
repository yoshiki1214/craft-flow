"""
POS機能の動作確認用スクリプト

実際のPDFファイルをアップロードして動作確認するためのヘルパースクリプトです。
"""

import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models.pos_sales import PosSales
from app.utils.pdf_processor import (
    extract_metadata_from_pdf,
    extract_table_data_from_pdf,
    parse_sales_data,
)
from app.features.pos import save_pdf_data_to_db


def test_pdf_upload(pdf_path: str, overwrite: bool = False):
    """
    PDFファイルのアップロード処理をテストする

    Args:
        pdf_path: PDFファイルのパス
        overwrite: 上書きオプション
    """
    if not os.path.exists(pdf_path):
        print(f"エラー: ファイルが見つかりません: {pdf_path}")
        return

    print(f"処理中: {pdf_path}")
    print("-" * 50)

    app = create_app()
    with app.app_context():
        # PDFからメタデータを抽出
        print("1. メタデータを抽出中...")
        metadata = extract_metadata_from_pdf(pdf_path)
        print(f"   レジ番号: {metadata.get('pos_number', 'N/A')}")
        print(f"   営業日: {metadata.get('sale_date', 'N/A')}")
        print(f"   出力日時: {metadata.get('reported_at', 'N/A')}")

        # PDFからテーブルデータを抽出
        print("2. テーブルデータを抽出中...")
        table_data = extract_table_data_from_pdf(pdf_path)
        print(f"   抽出した行数: {len(table_data)}")

        # データを整形
        print("3. データを整形中...")
        sales_records = parse_sales_data(table_data, metadata)
        print(f"   有効なレコード数: {len(sales_records)}")

        if sales_records:
            # DBに保存
            print("4. データベースに保存中...")
            filename = os.path.basename(pdf_path)
            stats = save_pdf_data_to_db(sales_records, filename, overwrite)
            print(f"   新規登録: {stats['inserted']}件")
            print(f"   スキップ: {stats['skipped']}件")
            print(f"   上書き: {stats['overwritten']}件")

            # データベースの状態を確認
            print("5. データベースの状態を確認中...")
            total_records = PosSales.query.count()
            unique_dates = db.session.query(PosSales.sale_date).distinct().count()
            unique_pos = db.session.query(PosSales.pos_number).distinct().count()
            print(f"   総レコード数: {total_records}")
            print(f"   営業日数: {unique_dates}")
            print(f"   POSレジ数: {unique_pos}")
        else:
            print("   エラー: 有効なレコードが抽出できませんでした")

    print("-" * 50)
    print("処理完了")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python scripts/test_upload.py <PDFファイルのパス> [--overwrite]")
        print("例: python scripts/test_upload.py C:\\Users\\e-tkh\\Downloads\\POSデータサンプル1.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]
    overwrite = "--overwrite" in sys.argv

    test_pdf_upload(pdf_path, overwrite)
