"""
PDFテキスト抽出スクリプト（デバッグ用）

PDFから抽出されたテキストをファイルに保存して確認します。
"""

import sys
import io
from pathlib import Path

# Windows環境でのエンコーディング問題を回避
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import pdfplumber

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python scripts/extract_pdf_text.py <PDFファイルのパス>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_file = "pdf_extracted_text.txt"

    print(f"PDFからテキストを抽出中: {pdf_path}")
    print(f"出力先: {output_file}")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            all_text = ""
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    all_text += f"=== ページ {i+1} ===\n"
                    all_text += page_text + "\n\n"

        # ファイルに保存
        with open(output_file, "w", encoding="utf-8", errors="replace") as f:
            f.write(all_text)

        print(f"抽出完了: {len(all_text)}文字")
        print(f"ファイルに保存しました: {output_file}")
        print("\n最初の500文字:")
        print("-" * 70)
        print(all_text[:500])

    except Exception as e:
        print(f"エラー: {e}")
        import traceback

        traceback.print_exc()
