"""
PDF処理ユーティリティ関数

PDFからデータを抽出し、整形するための関数群。
"""

import re
import sys
from datetime import datetime
from typing import Dict, List, Optional
import pdfplumber
import tabula
import pandas as pd


def convert_wareki_to_seireki(wareki_date: str) -> Optional[str]:
    """
    和暦の日付文字列を西暦（YYYY-MM-DD形式）に変換する

    Args:
        wareki_date: 和暦の日付文字列（例: "令和7年11月5日"）

    Returns:
        西暦の日付文字列（YYYY-MM-DD形式）、変換できない場合はNone
    """
    # 令和の開始年は2019年
    wareki_eras = {
        "令和": 2018,  # 令和1年 = 2019年なので、オフセットは2018
        "平成": 1988,  # 平成1年 = 1989年なので、オフセットは1988
        "昭和": 1925,  # 昭和1年 = 1926年なので、オフセットは1925
    }

    # パターン: 令和7年11月5日
    pattern = r"(令和|平成|昭和)(\d+)年(\d+)月(\d+)日"
    match = re.search(pattern, wareki_date)

    if not match:
        return None

    era_name, year_str, month_str, day_str = match.groups()

    if era_name not in wareki_eras:
        return None

    try:
        year = int(year_str) + wareki_eras[era_name]
        month = int(month_str)
        day = int(day_str)

        # 日付の妥当性チェック
        datetime(year, month, day)
        return f"{year:04d}-{month:02d}-{day:02d}"
    except (ValueError, TypeError):
        return None


def convert_wareki_datetime_to_seireki(wareki_datetime: str) -> Optional[str]:
    """
    和暦の日時文字列を西暦（YYYY-MM-DD HH:MM:SS形式）に変換する

    Args:
        wareki_datetime: 和暦の日時文字列（例: "令和7年11月6日 17時30分"）

    Returns:
        西暦の日時文字列（YYYY-MM-DD HH:MM:SS形式）、変換できない場合はNone
    """
    # パターン: 令和7年11月6日 17時30分
    pattern = r"(令和|平成|昭和)(\d+)年(\d+)月(\d+)日\s*(\d+)時(\d+)分"
    match = re.search(pattern, wareki_datetime)

    if match:
        era_name, year_str, month_str, day_str, hour_str, minute_str = match.groups()
        wareki_eras = {
            "令和": 2018,
            "平成": 1988,
            "昭和": 1925,
        }

        if era_name not in wareki_eras:
            return None

        try:
            year = int(year_str) + wareki_eras[era_name]
            month = int(month_str)
            day = int(day_str)
            hour = int(hour_str)
            minute = int(minute_str)

            # 日時の妥当性チェック
            datetime(year, month, day, hour, minute)
            return f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:00"
        except (ValueError, TypeError):
            return None

    # 時刻がない場合は日付のみを変換
    date_part = re.sub(r"\s+\d+時\d+分.*", "", wareki_datetime)
    date_str = convert_wareki_to_seireki(date_part)
    if date_str:
        return f"{date_str} 00:00:00"

    return None


def clean_price_string(price_str: str) -> int:
    """
    金額文字列から¥や,を除去し、INTEGER型に変換する

    Args:
        price_str: 金額文字列（例: "¥1,234" または "1,234"）

    Returns:
        整数値、変換できない場合は0
    """
    if not price_str or not isinstance(price_str, str):
        return 0

    # ¥、,、空白を除去
    cleaned = re.sub(r"[¥,\s]", "", str(price_str))

    try:
        return int(float(cleaned))
    except (ValueError, TypeError):
        return 0


def extract_metadata_from_pdf(pdf_path: str) -> Dict[str, Optional[str]]:
    """
    PDFからメタデータ（レジ番号、営業日、出力日時）を抽出する

    Args:
        pdf_path: PDFファイルのパス

    Returns:
        メタデータの辞書（pos_number, sale_date, reported_at）
    """
    metadata = {
        "pos_number": None,
        "sale_date": None,
        "reported_at": None,
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            # すべてのページからテキストを抽出（複数ページに対応）
            all_text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    all_text += page_text + "\n"

            if not all_text:
                print(f"[WARNING] PDFからテキストが抽出できませんでした: {pdf_path}")
                sys.stdout.flush()
                return metadata

            # デバッグ: 抽出したテキストの一部を表示（エンコーディングエラーを回避）
            try:
                safe_text = all_text[:500].encode("utf-8", errors="replace").decode("utf-8")
                print(f"[DEBUG] 抽出したテキスト（最初の500文字）: {safe_text}", flush=True)
            except Exception:
                print("[DEBUG] 抽出したテキスト（最初の500文字）: [表示できません]", flush=True)
            sys.stdout.flush()

            # レジ番号の抽出（例: POS1, POS 1, レジ番号：POS1 など）
            pos_patterns = [
                r"レジ番号[：:]\s*POS\s*(\d+)",  # レジ番号：POS1 の形式を優先
                r"POS\s*(\d+)",
                r"レジ[：:]\s*(\d+)",
            ]
            for pattern in pos_patterns:
                pos_match = re.search(pattern, all_text, re.IGNORECASE)
                if pos_match:
                    metadata["pos_number"] = f"POS{pos_match.group(1)}"
                    print(f"[DEBUG] レジ番号を抽出: {metadata['pos_number']}")
                    sys.stdout.flush()
                    break

            # 営業日の抽出（例: 令和7年11月5日）
            # 複数のパターンを試す（特殊文字に対応）
            # 「日」と「月」が特殊文字の場合があるため、任意の文字として扱う
            sale_date_patterns = [
                r"営業[^\d]*(令和|平成|昭和)(\d+)[^\d]+(\d+)[^\d]+(\d+)",  # 営業日：令和7年11月5日（特殊文字対応）
                r"営業[^\d]*(\d+)[^\d]+(\d+)[^\d]+(\d+)",  # 営業日の後に数字パターン（特殊文字対応）
                r"営業日[：:]\s*(令和|平成|昭和)(\d+)年(\d+)月(\d+)日",  # 営業日：令和7年11月5日
                r"営業日[^\d]*(\d+)年(\d+)月(\d+)日",  # 文字化け対応: 営業日の後に数字パターン
                r"(令和|平成|昭和)(\d+)年(\d+)月(\d+)日",  # 営業日のラベルがない場合
            ]

            for pattern in sale_date_patterns:
                sale_date_match = re.search(pattern, all_text)
                if sale_date_match:
                    # グループ数を確認
                    num_groups = len(sale_date_match.groups())
                    # 元号が含まれているかチェック（最初のグループが元号の場合）
                    has_era = num_groups == 4 and sale_date_match.group(1) in ["令和", "平成", "昭和"]

                    if num_groups == 3 and not has_era:
                        # 数字のみのパターン（令和などの元号がない場合、文字化け）
                        year, month, day = sale_date_match.groups()
                        try:
                            year_int = int(year)
                            month_int = int(month)
                            day_int = int(day)
                            # 令和の開始年は2019年、令和7年 = 2025年
                            if year_int <= 10:  # 令和の年号と仮定
                                year_int = 2018 + year_int  # 令和1年 = 2019年
                            elif year_int <= 32:  # 平成の年号と仮定
                                year_int = 1988 + year_int  # 平成1年 = 1989年
                            elif year_int <= 65:  # 昭和の年号と仮定
                                year_int = 1925 + year_int  # 昭和1年 = 1926年

                            from datetime import datetime

                            datetime(year_int, month_int, day_int)  # 日付の妥当性チェック
                            metadata["sale_date"] = f"{year_int:04d}-{month_int:02d}-{day_int:02d}"
                            print(f"[DEBUG] 日付を抽出（数字パターン）: {metadata['sale_date']}")
                            sys.stdout.flush()
                            break
                        except (ValueError, TypeError):
                            continue
                    elif has_era:
                        # 元号付きのパターン（4グループ: 元号, 年, 月, 日）
                        era, year, month, day = sale_date_match.groups()
                        sale_date_str = f"{era}{year}年{month}月{day}日"
                        converted = convert_wareki_to_seireki(sale_date_str)
                        if converted:
                            metadata["sale_date"] = converted
                            print(f"[DEBUG] 日付を抽出（元号パターン）: {metadata['sale_date']}")
                            sys.stdout.flush()
                            break
                    else:
                        # 元号付きのパターン（3グループ: 元号, 年, 月, 日 - ラベルなし）
                        sale_date_str = sale_date_match.group(0)
                        converted = convert_wareki_to_seireki(sale_date_str)
                        if converted:
                            metadata["sale_date"] = converted
                            print(f"[DEBUG] 日付を抽出（元号パターン・ラベルなし）: {metadata['sale_date']}")
                            sys.stdout.flush()
                            break

            # 出力日時の抽出（例: 令和7年11月6日 17時30分）
            # 「日」と「月」が特殊文字の場合があるため、任意の文字として扱う
            reported_patterns = [
                # 出力日時：令和7年11月6日 17時30分（特殊文字対応）
                r"出[^\d]*(令和|平成|昭和)(\d+)[^\d]+(\d+)[^\d]+(\d+)[^\d]*(\d+)時(\d+)分",
                # 出力日時の後に数字パターン（特殊文字対応）
                r"出[^\d]*(\d+)[^\d]+(\d+)[^\d]+(\d+)[^\d]*(\d+)時(\d+)分",
                # 出力日時：令和7年11月6日 17時30分（特殊文字対応）
                r"出力[^\d]*(令和|平成|昭和)(\d+)[^\d]+(\d+)[^\d]+(\d+)[^\d]*(\d+)時(\d+)分",
                # 出力日時の後に数字パターン（特殊文字対応）
                r"出力[^\d]*(\d+)[^\d]+(\d+)[^\d]+(\d+)[^\d]*(\d+)時(\d+)分",
                # 出力日時：令和7年11月6日 17時30分
                r"出力日時[：:]\s*(令和|平成|昭和)(\d+)年(\d+)月(\d+)日\s*(\d+)時(\d+)分",
                # 文字化け対応
                r"出力日時[^\d]*(\d+)年(\d+)月(\d+)日\s*(\d+)時(\d+)分",
                r"出力日[：:]\s*(令和|平成|昭和)(\d+)年(\d+)月(\d+)日\s*(\d+)時(\d+)分",
                r"出力日[^\d]*(\d+)年(\d+)月(\d+)日\s*(\d+)時(\d+)分",
            ]
            for pattern in reported_patterns:
                reported_match = re.search(pattern, all_text)
                if reported_match:
                    # グループ数を確認
                    num_groups = len(reported_match.groups())
                    # 元号が含まれているかチェック（最初のグループが元号の場合）
                    has_era = num_groups == 6 and reported_match.group(1) in ["令和", "平成", "昭和"]

                    if num_groups == 5 and not has_era:
                        # 数字のみのパターン（令和などの元号がない場合、文字化け）
                        year, month, day, hour, minute = reported_match.groups()
                        try:
                            year_int = int(year)
                            month_int = int(month)
                            day_int = int(day)
                            hour_int = int(hour)
                            minute_int = int(minute)
                            # 令和の開始年は2019年、令和7年 = 2025年
                            if year_int <= 10:  # 令和の年号と仮定
                                year_int = 2018 + year_int
                            elif year_int <= 32:  # 平成の年号と仮定
                                year_int = 1988 + year_int
                            elif year_int <= 65:  # 昭和の年号と仮定
                                year_int = 1925 + year_int

                            from datetime import datetime

                            datetime(year_int, month_int, day_int, hour_int, minute_int)
                            reported_at_str = (
                                f"{year_int:04d}-{month_int:02d}-{day_int:02d} "
                                f"{hour_int:02d}:{minute_int:02d}:00"
                            )
                            metadata["reported_at"] = reported_at_str
                            print(f"[DEBUG] 出力日時を抽出（数字パターン）: {metadata['reported_at']}")
                            sys.stdout.flush()
                            break
                        except (ValueError, TypeError):
                            continue
                    elif has_era:
                        # 元号付きのパターン（6グループ: 元号, 年, 月, 日, 時, 分）
                        era, year, month, day, hour, minute = reported_match.groups()
                        reported_str = f"{era}{year}年{month}月{day}日 {hour}時{minute}分"
                        converted = convert_wareki_datetime_to_seireki(reported_str)
                        if converted:
                            metadata["reported_at"] = converted
                            print(f"[DEBUG] 出力日時を抽出（元号パターン）: {metadata['reported_at']}")
                            sys.stdout.flush()
                            break
                    else:
                        # 元号付きのパターン（5グループ: 元号, 年, 月, 日, 時, 分 - ラベルなし）
                        reported_str = reported_match.group(0)
                        converted = convert_wareki_datetime_to_seireki(reported_str)
                        if converted:
                            metadata["reported_at"] = converted
                            print(
                                f"[DEBUG] 出力日時を抽出（元号パターン・ラベルなし）: {metadata['reported_at']}"
                            )
                            sys.stdout.flush()
                            break

            print(f"[DEBUG] 抽出したメタデータ: {metadata}")
            sys.stdout.flush()

    except Exception as e:
        import traceback

        print(f"[ERROR] PDFメタデータ抽出エラー: {e}")
        print(f"[ERROR] トレースバック:\n{traceback.format_exc()}")
        sys.stdout.flush()

    return metadata


def extract_table_data_from_pdf(pdf_path: str) -> List[Dict[str, any]]:
    """
    PDFからテーブルデータを抽出する

    Args:
        pdf_path: PDFファイルのパス

    Returns:
        抽出したテーブルデータのリスト
    """
    try:
        print(f"[DEBUG] テーブルデータ抽出開始: {pdf_path}", flush=True)
        import sys

        sys.stdout.flush()

        # まずtabula-pyを試す（Javaが必要）
        dfs = []
        try:
            print("[DEBUG] tabula-pyでストリームモードで抽出を試みます...", flush=True)
            sys.stdout.flush()
            dfs = tabula.read_pdf(
                pdf_path,
                pages="all",
                multiple_tables=True,
                pandas_options={"header": None},
                lattice=False,
                stream=True,
            )
            print(f"[DEBUG] ストリームモードで抽出: {len(dfs) if dfs else 0}個のテーブル", flush=True)
            sys.stdout.flush()
        except Exception as e:
            print(f"[DEBUG] tabula-pyでエラー（Javaが必要な可能性）: {e}", flush=True)
            sys.stdout.flush()
            # tabula-pyが失敗した場合、pdfplumberを使用
            print("[DEBUG] pdfplumberでテーブル抽出を試みます...", flush=True)
            sys.stdout.flush()

            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    tables = page.extract_tables()
                    if tables:
                        print(f"[DEBUG] ページ{page_num+1}で{len(tables)}個のテーブルを発見", flush=True)
                        sys.stdout.flush()
                        for table in tables:
                            # テーブルをDataFrameに変換
                            if table:
                                df = pd.DataFrame(table[1:], columns=table[0] if table else None)
                                dfs.append(df)

        if not dfs:
            print("[DEBUG] テーブルデータが抽出できませんでした", flush=True)
            sys.stdout.flush()
            return []

        # すべてのテーブルを結合
        all_data = []
        for i, df in enumerate(dfs):
            print(f"[DEBUG] テーブル{i+1}: {len(df)}行 x {len(df.columns)}列", flush=True)
            sys.stdout.flush()

            # 空のDataFrameをスキップ
            if df.empty:
                print(f"[DEBUG] テーブル{i+1}は空です", flush=True)
                sys.stdout.flush()
                continue

            # 最初の3行を表示（デバッグ用）
            if len(df) > 0:
                print(f"[DEBUG] テーブル{i+1}の最初の3行:", flush=True)
                for j in range(min(3, len(df))):
                    row_data = df.iloc[j].tolist()
                    print(f"  行{j+1}: {row_data}", flush=True)
                sys.stdout.flush()

            # データを辞書のリストに変換
            for _, row in df.iterrows():
                # 行が空でない場合のみ処理
                if not row.isna().all():
                    row_dict = {}
                    for col_idx, value in enumerate(row):
                        if pd.notna(value):
                            row_dict[f"col_{col_idx}"] = str(value).strip()
                    if row_dict:
                        all_data.append(row_dict)

        print(f"[DEBUG] 抽出したテーブルデータ: {len(all_data)}行", flush=True)
        sys.stdout.flush()
        return all_data

    except Exception as e:
        import traceback

        print(f"[ERROR] テーブルデータ抽出エラー: {e}", flush=True)
        print(f"[ERROR] トレースバック:\n{traceback.format_exc()}", flush=True)
        sys.stdout.flush()
        return []


def parse_sales_data(
    table_data: List[Dict[str, any]], metadata: Dict[str, Optional[str]]
) -> List[Dict[str, any]]:
    """
    抽出したテーブルデータを整形し、pos_salesテーブル用のデータに変換する

    Args:
        table_data: 抽出したテーブルデータ
        metadata: PDFから抽出したメタデータ

    Returns:
        整形された売上データのリスト
    """
    sales_records = []

    if not table_data:
        print("[WARNING] テーブルデータが空です", flush=True)
        sys.stdout.flush()
        return sales_records

    # デバッグ: 最初の数行のテーブルデータを表示
    print("[DEBUG] テーブルデータのサンプル（最初の3行）:", flush=True)
    for i, row in enumerate(table_data[:3]):
        print(f"  行{i+1}: {row}", flush=True)
    sys.stdout.flush()

    for row_idx, row in enumerate(table_data):
        # ヘッダー行をスキップ（商品コード、商品名などの文字列が含まれている行）
        col_0 = row.get("col_0", "").strip() if "col_0" in row else ""
        if col_0 in ["商品コード", "商品名", "単価", "数量", "小計"] or not col_0:
            print(f"[DEBUG] 行{row_idx+1}をスキップ: ヘッダー行または空行", flush=True)
            sys.stdout.flush()
            continue

        # 列の数を確認
        col_keys = [k for k in row.keys() if k.startswith("col_")]
        num_cols = len(col_keys)

        # 2列組のレイアウトを処理
        # 左列: col_0=商品コード, col_1=商品名, col_2=単価, col_3=数量, col_4=小計
        # 右列: col_5=商品コード, col_6=商品名, col_7=単価, col_8=数量, col_9=小計

        def create_record(left_or_right: str, col_offset: int) -> Dict[str, any]:
            """左列または右列からレコードを作成"""
            product_code = row.get(f"col_{col_offset}", "").strip() if f"col_{col_offset}" in row else ""
            product_name = row.get(f"col_{col_offset+1}", "").strip() if f"col_{col_offset+1}" in row else ""
            unit_price_str = (
                row.get(f"col_{col_offset+2}", "0").strip() if f"col_{col_offset+2}" in row else "0"
            )
            quantity_str = (
                row.get(f"col_{col_offset+3}", "0").strip() if f"col_{col_offset+3}" in row else "0"
            )
            subtotal_str = (
                row.get(f"col_{col_offset+4}", "0").strip() if f"col_{col_offset+4}" in row else "0"
            )

            # 商品コードと商品名が空の場合はNoneを返す
            if not product_code and not product_name:
                return None

            # 数量を数値に変換
            try:
                quantity = int(float(quantity_str)) if quantity_str else 0
            except (ValueError, TypeError):
                quantity = 0

            # 数量が0の場合はNoneを返す
            if quantity == 0:
                return None

            # 単価と小計を数値に変換
            unit_price = clean_price_string(unit_price_str)
            subtotal = clean_price_string(subtotal_str)

            # レコードを作成
            record = {
                "pos_number": metadata.get("pos_number", ""),
                "sale_date": metadata.get("sale_date", ""),
                "reported_at": metadata.get("reported_at", ""),
                "product_code": product_code,
                "product_name": product_name,
                "quantity": quantity,
                "unit_price": unit_price,
                "subtotal": subtotal,
                "total_amount": 0,  # 後で計算
            }

            return record

        # 左列からレコードを作成
        left_record = create_record("left", 0)
        if left_record:
            sales_records.append(left_record)
            product_name = left_record["product_name"]
            quantity = left_record["quantity"]
            print(
                f"[DEBUG] 行{row_idx+1}（左列）をレコードに追加: " f"{product_name} x{quantity}",
                flush=True,
            )
            sys.stdout.flush()

        # 右列からレコードを作成（2列組の場合）
        if num_cols >= 10:
            right_record = create_record("right", 5)
            if right_record:
                sales_records.append(right_record)
                right_product_name = right_record["product_name"]
                right_quantity = right_record["quantity"]
                print(
                    f"[DEBUG] 行{row_idx+1}（右列）をレコードに追加: "
                    f"{right_product_name} x{right_quantity}",
                    flush=True,
                )
                sys.stdout.flush()

    # 総合計金額を計算（同じPOSレジの全レコードで同じ値）
    if sales_records:
        # テーブルから総合計を抽出するか、小計の合計を使用
        total = sum(record["subtotal"] for record in sales_records)
        for record in sales_records:
            record["total_amount"] = total
        print(f"[DEBUG] 総合計金額: {total:,}円", flush=True)
        sys.stdout.flush()

    return sales_records
