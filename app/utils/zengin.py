"""全銀フォーマット変換ユーティリティ

全国銀行協会統一フォーマット（全銀フォーマット）への変換処理を提供
"""

from datetime import datetime
from typing import List, Dict, Optional, Tuple
import pandas as pd


class ZenginFormatError(Exception):
    """全銀フォーマット変換エラー"""
    pass


class ZenginConverter:
    """全銀フォーマット変換クラス"""
    
    # 全銀フォーマットのレコード長
    RECORD_LENGTH = 120
    
    # データレコードのフィールド定義（例）
    # 注意：実際の仕様書を参照して調整してください
    FIELD_DEFINITIONS = {
        'data_type': {'pos': 0, 'length': 1, 'default': '1', 'fill': '1'},  # データ区分
        'bank_code': {'pos': 1, 'length': 4, 'fill': '0', 'align': 'right'},  # 銀行コード
        'branch_code': {'pos': 5, 'length': 3, 'fill': '0', 'align': 'right'},  # 支店コード
        'account_type': {'pos': 8, 'length': 1, 'fill': '1', 'default': '1'},  # 預金種目（1=普通、2=当座）
        'account_number': {'pos': 9, 'length': 7, 'fill': '0', 'align': 'right'},  # 口座番号
        'recipient_name': {'pos': 16, 'length': 30, 'fill': ' ', 'align': 'left'},  # 受取人名（全角カナ）
        'amount': {'pos': 46, 'length': 10, 'fill': '0', 'align': 'right'},  # 振込金額
        'requester_code': {'pos': 56, 'length': 4, 'fill': ' ', 'align': 'left'},  # 依頼人コード
        'requester_name': {'pos': 60, 'length': 20, 'fill': ' ', 'align': 'left'},  # 依頼人名
        'new_code': {'pos': 80, 'length': 1, 'fill': '1', 'default': '1'},  # 新規コード
        'customer_code1': {'pos': 81, 'length': 7, 'fill': ' ', 'align': 'left'},  # 顧客番号1
        'customer_code2': {'pos': 88, 'length': 7, 'fill': ' ', 'align': 'left'},  # 顧客番号2
        'blank': {'pos': 95, 'length': 25, 'fill': ' ', 'align': 'left'},  # 余白
    }
    
    @staticmethod
    def _pad_string(value: str, length: int, fill_char: str = ' ', align: str = 'left') -> str:
        """
        文字列を指定長に調整（パディング）
        
        Args:
            value: パディング対象の文字列
            length: 目標長
            fill_char: 埋め込み文字
            align: 配置方向（'left'=左寄せ、'right'=右寄せ）
            
        Returns:
            パディング済み文字列
        """
        if len(value) > length:
            raise ZenginFormatError(f"文字列が長すぎます: {value} (長さ: {len(value)}, 最大: {length})")
        
        if align == 'right':
            return value.rjust(length, fill_char)
        else:
            return value.ljust(length, fill_char)
    
    @staticmethod
    def _validate_numeric(value: str, field_name: str, max_digits: Optional[int] = None) -> str:
        """
        数値フィールドの検証
        
        Args:
            value: 検証対象の値
            field_name: フィールド名（エラーメッセージ用）
            max_digits: 最大桁数
            
        Returns:
            検証済みの文字列
            
        Raises:
            ZenginFormatError: 検証失敗時
        """
        # NoneやNaNの処理
        if pd.isna(value) or value is None:
            raise ZenginFormatError(f"{field_name}が空です")
        
        # 文字列に変換
        str_value = str(value).strip()
        
        # 数値チェック
        if not str_value.isdigit():
            raise ZenginFormatError(f"{field_name}は数値である必要があります: {value}")
        
        # 桁数チェック
        if max_digits and len(str_value) > max_digits:
            raise ZenginFormatError(f"{field_name}の桁数が超過しています: {value} (最大: {max_digits}桁)")
        
        return str_value
    
    @classmethod
    def validate_customer_data(cls, row: Dict) -> Tuple[bool, List[str]]:
        """
        顧客データのバリデーション
        
        Args:
            row: 顧客データの辞書
            
        Returns:
            (検証結果, エラーメッセージリスト)
        """
        errors = []
        
        # 必須フィールドのチェック
        required_fields = ['bank_code', 'branch_code', 'account_number', 'recipient_name', 'amount']
        for field in required_fields:
            if field not in row or pd.isna(row[field]):
                errors.append(f"{field}が必須です")
        
        # 銀行コードの検証
        if 'bank_code' in row and not pd.isna(row['bank_code']):
            try:
                bank_code = cls._validate_numeric(row['bank_code'], '銀行コード', 4)
                if len(bank_code) > 4:
                    errors.append("銀行コードは4桁以内である必要があります")
            except ZenginFormatError as e:
                errors.append(str(e))
        
        # 支店コードの検証
        if 'branch_code' in row and not pd.isna(row['branch_code']):
            try:
                branch_code = cls._validate_numeric(row['branch_code'], '支店コード', 3)
                if len(branch_code) > 3:
                    errors.append("支店コードは3桁以内である必要があります")
            except ZenginFormatError as e:
                errors.append(str(e))
        
        # 口座番号の検証
        if 'account_number' in row and not pd.isna(row['account_number']):
            try:
                account_number = cls._validate_numeric(row['account_number'], '口座番号', 7)
                if len(account_number) > 7:
                    errors.append("口座番号は7桁以内である必要があります")
            except ZenginFormatError as e:
                errors.append(str(e))
        
        # 口座種別の検証
        if 'account_type' in row and not pd.isna(row['account_type']):
            account_type = str(row['account_type']).strip()
            # 「普通」「当座」という文字列も許可し、後で変換
            if account_type not in ['1', '2', '普通', '当座']:
                errors.append("口座種別は1（普通）または2（当座）である必要があります")
        
        # 振込金額の検証
        if 'amount' in row and not pd.isna(row['amount']):
            try:
                # 数値の場合はそのまま、文字列の場合は変換
                if isinstance(row['amount'], (int, float)):
                    amount_value = int(row['amount'])
                else:
                    amount_str = str(row['amount']).replace(',', '').strip()
                    amount_value = int(float(amount_str))
                
                if amount_value <= 0:
                    errors.append("振込金額は0より大きい必要があります")
            except (ValueError, TypeError) as e:
                errors.append(f"振込金額の形式が不正です: {row['amount']}")
        
        # 受取人名の検証（全角カナ想定）
        if 'recipient_name' in row and not pd.isna(row['recipient_name']):
            recipient_name = str(row['recipient_name']).strip()
            if len(recipient_name) == 0:
                errors.append("受取人名が空です")
            elif len(recipient_name) > 30:
                errors.append(f"受取人名が長すぎます（最大30文字）: {recipient_name}")
        
        return len(errors) == 0, errors
    
    @classmethod
    def convert_row_to_record(cls, row: Dict, requester_code: str = '', requester_name: str = '') -> str:
        """
        顧客データの1行を全銀フォーマットのレコードに変換
        
        Args:
            row: 顧客データの辞書
            requester_code: 依頼人コード（オプション）
            requester_name: 依頼人名（オプション）
            
        Returns:
            全銀フォーマットの120文字固定長レコード
            
        Raises:
            ZenginFormatError: 変換エラー時
        """
        # バリデーション
        is_valid, errors = cls.validate_customer_data(row)
        if not is_valid:
            raise ZenginFormatError(f"データ検証エラー: {', '.join(errors)}")
        
        # レコードを初期化（スペースで埋める）
        record = [' '] * cls.RECORD_LENGTH
        
        # 各フィールドを設定
        defs = cls.FIELD_DEFINITIONS
        
        # データ区分
        record[defs['data_type']['pos']] = defs['data_type']['default']
        
        # 銀行コード（4桁、右寄せゼロ埋め）
        bank_code = cls._validate_numeric(row['bank_code'], '銀行コード', 4)
        bank_code_str = cls._pad_string(bank_code, 4, '0', 'right')
        for i, char in enumerate(bank_code_str):
            record[defs['bank_code']['pos'] + i] = char
        
        # 支店コード（3桁、右寄せゼロ埋め）
        branch_code = cls._validate_numeric(row['branch_code'], '支店コード', 3)
        branch_code_str = cls._pad_string(branch_code, 3, '0', 'right')
        for i, char in enumerate(branch_code_str):
            record[defs['branch_code']['pos'] + i] = char
        
        # 口座種別（1桁）
        account_type = str(row.get('account_type', '1')).strip()
        # 「普通」「当座」という文字列を数値に変換
        if account_type == '普通' or account_type.lower() == 'futsu':
            account_type = '1'
        elif account_type == '当座' or account_type.lower() == 'toza':
            account_type = '2'
        elif account_type not in ['1', '2']:
            account_type = '1'  # デフォルトは普通
        record[defs['account_type']['pos']] = account_type
        
        # 口座番号（7桁、右寄せゼロ埋め）
        account_number = cls._validate_numeric(row['account_number'], '口座番号', 7)
        account_number_str = cls._pad_string(account_number, 7, '0', 'right')
        for i, char in enumerate(account_number_str):
            record[defs['account_number']['pos'] + i] = char
        
        # 受取人名（30桁、左寄せスペース埋め、全角カナ）
        recipient_name = str(row['recipient_name']).strip()
        recipient_name_str = cls._pad_string(recipient_name, 30, ' ', 'left')
        for i, char in enumerate(recipient_name_str):
            if defs['recipient_name']['pos'] + i < cls.RECORD_LENGTH:
                record[defs['recipient_name']['pos'] + i] = char
        
        # 振込金額（10桁、右寄せゼロ埋め）
        # 数値の場合はそのまま、文字列の場合は変換
        if isinstance(row['amount'], (int, float)):
            amount_value = int(row['amount'])
        else:
            amount_str_raw = str(row['amount']).replace(',', '').strip()
            amount_value = int(float(amount_str_raw))
        
        amount_str = cls._pad_string(str(amount_value), 10, '0', 'right')
        for i, char in enumerate(amount_str):
            record[defs['amount']['pos'] + i] = char
        
        # 依頼人コード（4桁、左寄せスペース埋め）
        req_code = str(requester_code).strip()[:4]
        req_code_str = cls._pad_string(req_code, 4, ' ', 'left')
        for i, char in enumerate(req_code_str):
            record[defs['requester_code']['pos'] + i] = char
        
        # 依頼人名（20桁、左寄せスペース埋め）
        req_name = str(requester_name).strip()[:20]
        req_name_str = cls._pad_string(req_name, 20, ' ', 'left')
        for i, char in enumerate(req_name_str):
            record[defs['requester_name']['pos'] + i] = char
        
        # 新規コード
        record[defs['new_code']['pos']] = defs['new_code']['default']
        
        # 顧客番号1（7桁、左寄せスペース埋め）
        customer_code1 = str(row.get('customer_code1', '')).strip()[:7]
        customer_code1_str = cls._pad_string(customer_code1, 7, ' ', 'left')
        for i, char in enumerate(customer_code1_str):
            record[defs['customer_code1']['pos'] + i] = char
        
        # 顧客番号2（7桁、左寄せスペース埋め）
        customer_code2 = str(row.get('customer_code2', '')).strip()[:7]
        customer_code2_str = cls._pad_string(customer_code2, 7, ' ', 'left')
        for i, char in enumerate(customer_code2_str):
            record[defs['customer_code2']['pos'] + i] = char
        
        # 余白は既にスペースで埋められている
        
        return ''.join(record)
    
    @classmethod
    def create_header_record(cls, record_count: int, date: Optional[datetime] = None) -> str:
        """
        ヘッダーレコードを作成
        
        Args:
            record_count: データレコード数
            date: 処理日付（デフォルト: 今日）
            
        Returns:
            ヘッダーレコード（120文字固定長）
        """
        if date is None:
            date = datetime.now()
        
        record = [' '] * cls.RECORD_LENGTH
        
        # ヘッダーレコードの形式（例）
        # 実際の仕様書に従って調整してください
        # データ区分: 0（ヘッダー）
        record[0] = '0'
        
        # 日付: YYYYMMDD
        date_str = date.strftime('%Y%m%d')
        for i, char in enumerate(date_str):
            if i < 8:
                record[1 + i] = char
        
        # レコード数
        record_count_str = cls._pad_string(str(record_count), 6, '0', 'right')
        for i, char in enumerate(record_count_str):
            if i < 6:
                record[9 + i] = char
        
        return ''.join(record)
    
    @classmethod
    def create_trailer_record(cls, record_count: int, total_amount: int) -> str:
        """
        トレーラーレコードを作成
        
        Args:
            record_count: データレコード数
            total_amount: 合計金額
            
        Returns:
            トレーラーレコード（120文字固定長）
        """
        record = [' '] * cls.RECORD_LENGTH
        
        # トレーラーレコードの形式（例）
        # 実際の仕様書に従って調整してください
        # データ区分: 9（トレーラー）
        record[0] = '9'
        
        # レコード数
        record_count_str = cls._pad_string(str(record_count), 6, '0', 'right')
        for i, char in enumerate(record_count_str):
            if i < 6:
                record[1 + i] = char
        
        # 合計金額（10桁、右寄せゼロ埋め）
        total_amount_str = cls._pad_string(str(total_amount), 10, '0', 'right')
        for i, char in enumerate(total_amount_str):
            if i < 10:
                record[7 + i] = char
        
        return ''.join(record)
    
    @classmethod
    def _normalize_column_names(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        列名を標準化（日本語→英語へのマッピング）
        
        Args:
            df: DataFrame
            
        Returns:
            列名を標準化したDataFrame
        """
        # 日本語列名から英語列名へのマッピング
        column_mapping = {
            '金融機関コード': 'bank_code',
            '銀行コード': 'bank_code',
            '支店コード': 'branch_code',
            '預金種目': 'account_type',
            '口座種目': 'account_type',
            '口座番号': 'account_number',
            '口座名義（カナ）': 'recipient_name',
            '口座名義(カナ)': 'recipient_name',
            '受取人名': 'recipient_name',
            '振込金額': 'amount',
            '金額': 'amount',
            '顧客ID': 'customer_code1',
            '顧客番号': 'customer_code1',
        }
        
        # 列名を標準化（空白を削除）
        df.columns = df.columns.str.strip()
        
        # マッピングに従って列名を変換
        df = df.rename(columns=column_mapping)
        
        return df
    
    @classmethod
    def convert_excel_to_zengin(
        cls,
        excel_path: str,
        sheet_name: Optional[str] = None,
        requester_code: str = '',
        requester_name: str = ''
    ) -> List[str]:
        """
        Excelファイルを全銀フォーマットに変換
        
        Args:
            excel_path: Excelファイルのパス
            sheet_name: シート名（Noneの場合は最初のシート）
            requester_code: 依頼人コード
            requester_name: 依頼人名
            
        Returns:
            全銀フォーマットのレコードリスト
            
        Raises:
            ZenginFormatError: 変換エラー時
        """
        try:
            # Excelファイルを読み込む
            # sheet_nameがNoneの場合は最初のシートを読み込む
            if sheet_name is None:
                df = pd.read_excel(excel_path, sheet_name=0)
            else:
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
            
            # dfが辞書の場合は最初のシートを使用（複数シート読み込みの場合）
            if isinstance(df, dict):
                if not df:
                    raise ZenginFormatError("Excelファイルにシートがありません")
                # 最初のシートを使用
                first_sheet_name = list(df.keys())[0]
                df = df[first_sheet_name]
            
            if df.empty:
                raise ZenginFormatError("Excelファイルが空です")
            
            # 列名を標準化（日本語→英語へのマッピング）
            df = cls._normalize_column_names(df)
            
            records = []
            total_amount = 0
            error_rows = []
            total_rows = len(df)
            
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f'データ変換開始: 合計{total_rows}行を処理します')
            
            # 各行を処理
            for idx, row in df.iterrows():
                try:
                    # 進捗ログ（10行ごと、または最初の数行）
                    if idx < 5 or idx % 10 == 0:
                        logger.info(f'処理中: {idx + 1}/{total_rows}行目')
                    
                    row_dict = row.to_dict()
                    record = cls.convert_row_to_record(row_dict, requester_code, requester_name)
                    records.append(record)
                    
                    # 合計金額を計算
                    try:
                        amount_value = row_dict.get('amount', 0)
                        # 数値でない場合（文字列など）は変換を試みる
                        if pd.notna(amount_value):
                            amount = int(float(str(amount_value).replace(',', '')))
                            total_amount += amount
                    except (ValueError, TypeError) as e:
                        # 金額計算エラーは警告のみ（処理は続行）
                        pass
                    
                except ZenginFormatError as e:
                    error_rows.append(f"行 {idx + 2}: {str(e)}")  # +2はヘッダー行と0ベースインデックスのため
                    continue
                except Exception as e:
                    # 予期しないエラーも記録
                    error_rows.append(f"行 {idx + 2}: 予期しないエラー - {str(e)}")
                    continue
            
            if not records:
                raise ZenginFormatError("変換可能なデータがありません")
            
            if error_rows:
                raise ZenginFormatError(f"変換エラーが発生しました:\n" + "\n".join(error_rows[:10]))  # 最大10件まで表示
            
            # ヘッダーレコードを先頭に追加
            header = cls.create_header_record(len(records))
            records.insert(0, header)
            
            # トレーラーレコードを末尾に追加
            trailer = cls.create_trailer_record(len(records) - 2, total_amount)  # -2はヘッダーとトレーラーを除く
            records.append(trailer)
            
            return records
            
        except FileNotFoundError:
            raise ZenginFormatError(f"ファイルが見つかりません: {excel_path}")
        except pd.errors.EmptyDataError:
            raise ZenginFormatError("Excelファイルが空です")
        except Exception as e:
            raise ZenginFormatError(f"ファイル読み込みエラー: {str(e)}")

