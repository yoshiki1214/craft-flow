"""
PDFメタデータ抽出テストスクリプト

実際のPDFファイルからメタデータが正しく抽出できるかテストします。
"""

import sys
import io
from pathlib import Path

# Windows環境でのエンコーディング問題を回避
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pdfplumber
from app.utils.pdf_processor import extract_metadata_from_pdf, convert_wareki_to_seireki


def test_pdf_metadata(pdf_path: str):
    """
    PDFファイルのメタデータ抽出をテストする

    Args:
        pdf_path: PDFファイルのパス
    """
    print("=" * 70)
    print(f"PDFメタデータ抽出テスト: {pdf_path}")
    print("=" * 70)

    # 1. pdfplumberでテキストを抽出
    print("\n[1] PDFからテキストを抽出")
    print("-" * 70)
    try:
        with pdfplumber.open(pdf_path) as pdf:
            all_text = ""
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    all_text += page_text + "\n"
                    print(f"ページ{i+1}: {len(page_text)}文字")

            if not all_text:
                print("エラー: テキストが抽出できませんでした")
                return

            print(f"\n抽出したテキスト（全{len(all_text)}文字）:")
            print("-" * 70)
            # エンコーディングエラーを回避
            try:
                print(all_text[:1000])  # 最初の1000文字を表示
            except UnicodeEncodeError:
                # エンコードできない文字を置換
                safe_text = all_text[:1000].encode("utf-8", errors="replace").decode("utf-8")
                print(safe_text)
            if len(all_text) > 1000:
                print(f"\n... (残り{len(all_text)-1000}文字)")

    except Exception as e:
        print(f"エラー: {e}")
        import traceback

        traceback.print_exc()
        return

    # 2. メタデータ抽出関数を実行
    print("\n[2] メタデータ抽出関数の実行")
    print("-" * 70)
    metadata = extract_metadata_from_pdf(pdf_path)
    print(f"結果: {metadata}")

    # 3. 手動でパターンマッチングをテスト
    print("\n[3] 手動パターンマッチングテスト")
    print("-" * 70)
    import re

    # レジ番号のパターン
    pos_patterns = [
        r"POS\s*(\d+)",
        r"レジ番号[：:]\s*POS\s*(\d+)",
        r"レジ[：:]\s*(\d+)",
    ]
    print("レジ番号の検索:")
    for pattern in pos_patterns:
        match = re.search(pattern, all_text, re.IGNORECASE)
        if match:
            print(f"  マッチ: {pattern} -> POS{match.group(1)}")
        else:
            print(f"  マッチなし: {pattern}")

    # 営業日のパターン
    sale_date_patterns = [
        r"営業日[：:]\s*(令和|平成|昭和)(\d+)年(\d+)月(\d+)日",
        r"(令和|平成|昭和)(\d+)年(\d+)月(\d+)日",
    ]
    print("\n営業日の検索:")
    for pattern in sale_date_patterns:
        match = re.search(pattern, all_text)
        if match:
            print(f"  マッチ: {pattern} -> {match.group(0)}")
            converted = convert_wareki_to_seireki(match.group(0))
            print(f"    変換後: {converted}")
        else:
            print(f"  マッチなし: {pattern}")

    # 出力日時のパターン
    reported_patterns = [
        r"出力日時[：:]\s*(令和|平成|昭和)(\d+)年(\d+)月(\d+)日\s*(\d+)時(\d+)分",
        r"出力日[：:]\s*(令和|平成|昭和)(\d+)年(\d+)月(\d+)日\s*(\d+)時(\d+)分",
    ]
    print("\n出力日時の検索:")
    for pattern in reported_patterns:
        match = re.search(pattern, all_text)
        if match:
            print(f"  マッチ: {pattern} -> {match.group(0)}")
        else:
            print(f"  マッチなし: {pattern}")

    print("\n" + "=" * 70)
    print("テスト完了")
    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python scripts/test_pdf_metadata.py <PDFファイルのパス>")
        print("例: python scripts/test_pdf_metadata.py C:\\Users\\e-tkh\\Downloads\\POS1.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]
    test_pdf_metadata(pdf_path)
