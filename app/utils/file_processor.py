"""
ファイル処理ユーティリティ

Excel/CSVファイルの読み込みとデータ変換処理を提供します。
"""

import pandas as pd
import io
from typing import List, Dict, Tuple, Optional
from werkzeug.datastructures import FileStorage


# 必須列名のマッピング（複数の表記に対応）
REQUIRED_COLUMNS = {
    'customer_name': ['顧客名', 'customer_name', '顧客', '名前', '事業者名', '代表者氏名'],
    'bank_name': ['銀行名', 'bank_name', '銀行', '金融機関名'],
    'bank_code': ['銀行コード', 'bank_code', '銀行コード', '金融機関コード'],
    'branch_name': ['支店名', 'branch_name', '支店'],
    'branch_code': ['支店コード', 'branch_code', '支店コード'],
    'account_type': ['口座種別', 'account_type', '口座タイプ', '種別', '預金種目'],
    'account_number': ['口座番号', 'account_number', '口座', '番号'],
    'transfer_amount': ['振込金額', 'transfer_amount', '金額', '振込', '金額']
}

# 銀行名・支店名からコードへの簡易マッピング（将来的にデータベースに移行可能）
# 実際の運用では、銀行名・支店名のマスタテーブルが必要
BANK_NAME_TO_CODE: Dict[str, str] = {}
BRANCH_NAME_TO_CODE: Dict[Tuple[str, str], str] = {}  # (銀行名, 支店名) -> 支店コード

# 口座種別のマッピング
ACCOUNT_TYPE_MAPPING = {
    '普通': '1',
    '当座': '2',
    '貯蓄': '4',
    '1': '1',
    '2': '2',
    '4': '4',
    '普通預金': '1',
    '当座預金': '2',
    '貯蓄預金': '4'
}


class FileProcessorError(Exception):
    """
    ファイル処理エラー

    ファイル処理中に発生したエラーを表します。
    """
    pass


def normalize_column_name(df: pd.DataFrame) -> pd.DataFrame:
    """
    列名を正規化する

    Args:
        df: データフレーム

    Returns:
        pd.DataFrame: 列名が正規化されたデータフレーム
    """
    # 列名の前後の空白を削除
    df.columns = df.columns.str.strip()
    
    # 列名マッピングを作成
    column_mapping = {}
    for standard_name, possible_names in REQUIRED_COLUMNS.items():
        for col in df.columns:
            if col in possible_names:
                # 既にマッピングされている場合はスキップ
                if col not in column_mapping:
                    column_mapping[col] = standard_name
                break
    
    # 列名をリネーム
    df = df.rename(columns=column_mapping)
    
    return df


def validate_required_columns(df: pd.DataFrame) -> List[str]:
    """
    必須列の存在をチェック

    Args:
        df: データフレーム

    Returns:
        List[str]: エラーメッセージのリスト（空の場合は正常）
    """
    errors = []
    
    # 必須列: 顧客名、口座種別、口座番号、振込金額
    required_cols = ['customer_name', 'account_type', 'account_number', 'transfer_amount']
    for col in required_cols:
        if col not in df.columns:
            possible_names = ', '.join(REQUIRED_COLUMNS[col])
            errors.append(f'必須列「{possible_names}」が見つかりません。')
    
    # 銀行情報: 銀行名または銀行コードのいずれかが必要
    has_bank_code = 'bank_code' in df.columns
    has_bank_name = 'bank_name' in df.columns
    if not has_bank_code and not has_bank_name:
        errors.append('必須列「銀行名」または「銀行コード」が見つかりません。')
    
    # 支店情報: 支店名または支店コードのいずれかが必要
    has_branch_code = 'branch_code' in df.columns
    has_branch_name = 'branch_name' in df.columns
    if not has_branch_code and not has_branch_name:
        errors.append('必須列「支店名」または「支店コード」が見つかりません。')
    
    return errors


def convert_account_type(value: any) -> Optional[str]:
    """
    口座種別を変換

    Args:
        value: 口座種別の値（文字列または数値）

    Returns:
        Optional[str]: 変換後の口座種別（1, 2, 4）、変換できない場合はNone
    """
    if pd.isna(value):
        return None
    
    # 文字列に変換
    value_str = str(value).strip()
    
    # マッピングテーブルから検索
    if value_str in ACCOUNT_TYPE_MAPPING:
        return ACCOUNT_TYPE_MAPPING[value_str]
    
    return None


def normalize_bank_code(bank_code_value: any) -> Optional[str]:
    """
    銀行コードを正規化（4桁の文字列に変換）

    Args:
        bank_code_value: 銀行コードの値（文字列、整数、浮動小数点）

    Returns:
        Optional[str]: 正規化された銀行コード（4桁）、変換できない場合はNone
    """
    if pd.isna(bank_code_value):
        return None
    
    # 整数型の場合は文字列に変換
    if isinstance(bank_code_value, (int, float)):
        bank_code_str = str(int(bank_code_value))
    else:
        bank_code_str = str(bank_code_value).strip()
    
    # 数字以外の文字が含まれている場合はNoneを返す
    if not bank_code_str or not bank_code_str.isdigit():
        return None
    
    # 4桁未満の場合はゼロパディング
    if len(bank_code_str) < 4:
        return bank_code_str.zfill(4)
    # 4桁の場合はそのまま返す
    elif len(bank_code_str) == 4:
        return bank_code_str
    # 4桁を超える場合は下4桁を使用
    else:
        return bank_code_str[-4:]


def normalize_branch_code(branch_code_value: any) -> Optional[str]:
    """
    支店コードを正規化（3桁の文字列に変換）

    Args:
        branch_code_value: 支店コードの値（文字列、整数、浮動小数点）

    Returns:
        Optional[str]: 正規化された支店コード（3桁）、変換できない場合はNone
    """
    if pd.isna(branch_code_value):
        return None
    
    # 整数型の場合は文字列に変換
    if isinstance(branch_code_value, (int, float)):
        branch_code_str = str(int(branch_code_value))
    else:
        branch_code_str = str(branch_code_value).strip()
    
    # 数字以外の文字が含まれている場合はNoneを返す
    if not branch_code_str or not branch_code_str.isdigit():
        return None
    
    # 3桁未満の場合はゼロパディング
    if len(branch_code_str) < 3:
        return branch_code_str.zfill(3)
    # 3桁の場合はそのまま返す
    elif len(branch_code_str) == 3:
        return branch_code_str
    # 3桁を超える場合は下3桁を使用
    else:
        return branch_code_str[-3:]


def normalize_account_number(account_number_value: any) -> Optional[str]:
    """
    口座番号を正規化（7桁の文字列に変換）

    Args:
        account_number_value: 口座番号の値（文字列、整数、浮動小数点）

    Returns:
        Optional[str]: 正規化された口座番号（7桁）、変換できない場合はNone
    """
    if pd.isna(account_number_value):
        return None
    
    # 整数型の場合は文字列に変換
    if isinstance(account_number_value, (int, float)):
        account_number_str = str(int(account_number_value))
    else:
        account_number_str = str(account_number_value).strip()
    
    # 数字以外の文字が含まれている場合はNoneを返す
    if not account_number_str or not account_number_str.isdigit():
        return None
    
    # 7桁未満の場合はゼロパディング
    if len(account_number_str) < 7:
        return account_number_str.zfill(7)
    # 7桁の場合はそのまま返す
    elif len(account_number_str) == 7:
        return account_number_str
    # 7桁を超える場合は下7桁を使用
    else:
        return account_number_str[-7:]


def convert_bank_name_to_code(bank_name: str) -> Optional[str]:
    """
    銀行名を銀行コードに変換

    Args:
        bank_name: 銀行名

    Returns:
        Optional[str]: 銀行コード（4桁）、変換できない場合はNone

    Note:
        将来的にデータベースのマスタテーブルから取得するように変更可能
    """
    if pd.isna(bank_name):
        return None
    
    bank_name_str = str(bank_name).strip()
    
    # マッピングテーブルから検索
    if bank_name_str in BANK_NAME_TO_CODE:
        return BANK_NAME_TO_CODE[bank_name_str]
    
    # 既にコード形式（4桁数字）の場合はそのまま返す
    if isinstance(bank_name_str, str) and len(bank_name_str) == 4 and bank_name_str.isdigit():
        return bank_name_str
    
    # マッピングが見つからない場合はNoneを返す
    # 実際の運用では、エラーとして扱うか、マスタテーブルを参照する
    return None


def convert_branch_name_to_code(bank_name: str, branch_name: str) -> Optional[str]:
    """
    支店名を支店コードに変換

    Args:
        bank_name: 銀行名
        branch_name: 支店名

    Returns:
        Optional[str]: 支店コード（3桁）、変換できない場合はNone

    Note:
        将来的にデータベースのマスタテーブルから取得するように変更可能
    """
    if pd.isna(branch_name):
        return None
    
    branch_name_str = str(branch_name).strip()
    bank_name_str = str(bank_name).strip() if not pd.isna(bank_name) else ''
    
    # マッピングテーブルから検索
    key = (bank_name_str, branch_name_str)
    if key in BRANCH_NAME_TO_CODE:
        return BRANCH_NAME_TO_CODE[key]
    
    # 既にコード形式（3桁数字）の場合はそのまま返す
    if isinstance(branch_name_str, str) and len(branch_name_str) == 3 and branch_name_str.isdigit():
        return branch_name_str
    
    # マッピングが見つからない場合はNoneを返す
    # 実際の運用では、エラーとして扱うか、マスタテーブルを参照する
    return None


def process_excel_file(file: FileStorage) -> Tuple[pd.DataFrame, List[str]]:
    """
    Excelファイルを読み込んで処理

    Args:
        file: アップロードされたファイル

    Returns:
        Tuple[pd.DataFrame, List[str]]: (データフレーム, エラーメッセージのリスト)
    """
    errors = []
    
    try:
        # ファイルを読み込み
        df = pd.read_excel(file, engine='openpyxl')
        
        # 列名を正規化
        df = normalize_column_name(df)
        
        # 必須列のチェック
        column_errors = validate_required_columns(df)
        if column_errors:
            errors.extend(column_errors)
            return pd.DataFrame(), errors
        
        # 空の行を削除
        df = df.dropna(how='all')
        
        # データ型の変換とバリデーション
        processed_data = []
        for idx, row in df.iterrows():
            row_errors = []
            row_num = idx + 2  # Excelの行番号（ヘッダー行を考慮）
            
            # 顧客名
            customer_name = str(row['customer_name']).strip() if not pd.isna(row.get('customer_name')) else None
            if not customer_name:
                row_errors.append(f'行{row_num}: 顧客名が空です。')
            
            # 銀行コード（銀行コード列を優先）
            bank_code = None
            bank_name = row.get('bank_name')
            if 'bank_code' in df.columns:
                bank_code_value = row.get('bank_code')
                bank_code = normalize_bank_code(bank_code_value)
                if not bank_code:
                    row_errors.append(f'行{row_num}: 銀行コードが無効です（4桁の数字である必要があります）: {bank_code_value}')
            elif bank_name:
                # 銀行コード列がない場合は銀行名から変換を試みる
                bank_code = convert_bank_name_to_code(bank_name)
                if not bank_code:
                    row_errors.append(f'行{row_num}: 銀行名「{bank_name}」から銀行コードを取得できませんでした。')
            else:
                row_errors.append(f'行{row_num}: 銀行コードまたは銀行名が必要です。')
            
            # 支店コード（支店コード列を優先）
            branch_code = None
            branch_name = row.get('branch_name')
            if 'branch_code' in df.columns:
                branch_code_value = row.get('branch_code')
                branch_code = normalize_branch_code(branch_code_value)
                if not branch_code:
                    row_errors.append(f'行{row_num}: 支店コードが無効です（3桁の数字である必要があります）: {branch_code_value}')
            elif branch_name:
                # 支店コード列がない場合は支店名から変換を試みる
                branch_code = convert_branch_name_to_code(bank_name, branch_name)
                if not branch_code:
                    row_errors.append(f'行{row_num}: 支店名「{branch_name}」から支店コードを取得できませんでした。')
            else:
                row_errors.append(f'行{row_num}: 支店コードまたは支店名が必要です。')
            
            # 口座種別
            account_type = convert_account_type(row.get('account_type'))
            if not account_type:
                row_errors.append(f'行{row_num}: 口座種別が無効です（普通、当座、貯蓄、または1、2、4である必要があります）。')
            
            # 口座番号
            account_number_value = row.get('account_number')
            account_number = normalize_account_number(account_number_value)
            if not account_number:
                if pd.isna(account_number_value):
                    row_errors.append(f'行{row_num}: 口座番号が空です。')
                else:
                    row_errors.append(f'行{row_num}: 口座番号が無効です（7桁の数字である必要があります）: {account_number_value}')
            
            # 振込金額
            transfer_amount = row.get('transfer_amount')
            if pd.isna(transfer_amount):
                row_errors.append(f'行{row_num}: 振込金額が空です。')
            else:
                try:
                    transfer_amount = int(float(transfer_amount))
                    if transfer_amount < 0:
                        row_errors.append(f'行{row_num}: 振込金額は0以上である必要があります。')
                except (ValueError, TypeError):
                    row_errors.append(f'行{row_num}: 振込金額が無効です（数値である必要があります）。')
            
            if row_errors:
                errors.extend(row_errors)
            else:
                processed_data.append({
                    'customer_name': customer_name,
                    'bank_code': bank_code,
                    'branch_code': branch_code,
                    'account_type': account_type,
                    'account_number': account_number,
                    'transfer_amount': transfer_amount
                })
        
        if errors:
            return pd.DataFrame(), errors
        
        return pd.DataFrame(processed_data), []
    
    except Exception as e:
        errors.append(f'Excelファイルの読み込み中にエラーが発生しました: {str(e)}')
        return pd.DataFrame(), errors


def process_csv_file(file: FileStorage, encoding: str = 'utf-8') -> Tuple[pd.DataFrame, List[str]]:
    """
    CSVファイルを読み込んで処理

    Args:
        file: アップロードされたファイル
        encoding: 文字コード（デフォルト: utf-8、Shift-JISの場合は 'shift-jis'）

    Returns:
        Tuple[pd.DataFrame, List[str]]: (データフレーム, エラーメッセージのリスト)
    """
    errors = []
    
    try:
        # まずUTF-8で試す
        try:
            file.seek(0)
            df = pd.read_csv(file, encoding=encoding)
        except UnicodeDecodeError:
            # UTF-8で読めない場合はShift-JISで試す
            file.seek(0)
            df = pd.read_csv(file, encoding='shift-jis')
        
        # 列名を正規化
        df = normalize_column_name(df)
        
        # 必須列のチェック
        column_errors = validate_required_columns(df)
        if column_errors:
            errors.extend(column_errors)
            return pd.DataFrame(), errors
        
        # 空の行を削除
        df = df.dropna(how='all')
        
        # データ型の変換とバリデーション（Excelと同じ処理）
        processed_data = []
        for idx, row in df.iterrows():
            row_errors = []
            row_num = idx + 2  # CSVの行番号（ヘッダー行を考慮）
            
            # 顧客名
            customer_name = str(row['customer_name']).strip() if not pd.isna(row.get('customer_name')) else None
            if not customer_name:
                row_errors.append(f'行{row_num}: 顧客名が空です。')
            
            # 銀行コード（銀行コード列を優先）
            bank_code = None
            bank_name = row.get('bank_name')
            if 'bank_code' in df.columns:
                bank_code_value = row.get('bank_code')
                bank_code = normalize_bank_code(bank_code_value)
                if not bank_code:
                    row_errors.append(f'行{row_num}: 銀行コードが無効です（4桁の数字である必要があります）: {bank_code_value}')
            elif bank_name:
                # 銀行コード列がない場合は銀行名から変換を試みる
                bank_code = convert_bank_name_to_code(bank_name)
                if not bank_code:
                    row_errors.append(f'行{row_num}: 銀行名「{bank_name}」から銀行コードを取得できませんでした。')
            else:
                row_errors.append(f'行{row_num}: 銀行コードまたは銀行名が必要です。')
            
            # 支店コード（支店コード列を優先）
            branch_code = None
            branch_name = row.get('branch_name')
            if 'branch_code' in df.columns:
                branch_code_value = row.get('branch_code')
                branch_code = normalize_branch_code(branch_code_value)
                if not branch_code:
                    row_errors.append(f'行{row_num}: 支店コードが無効です（3桁の数字である必要があります）: {branch_code_value}')
            elif branch_name:
                # 支店コード列がない場合は支店名から変換を試みる
                branch_code = convert_branch_name_to_code(bank_name, branch_name)
                if not branch_code:
                    row_errors.append(f'行{row_num}: 支店名「{branch_name}」から支店コードを取得できませんでした。')
            else:
                row_errors.append(f'行{row_num}: 支店コードまたは支店名が必要です。')
            
            # 口座種別
            account_type = convert_account_type(row.get('account_type'))
            if not account_type:
                row_errors.append(f'行{row_num}: 口座種別が無効です（普通、当座、貯蓄、または1、2、4である必要があります）。')
            
            # 口座番号
            account_number_value = row.get('account_number')
            account_number = normalize_account_number(account_number_value)
            if not account_number:
                if pd.isna(account_number_value):
                    row_errors.append(f'行{row_num}: 口座番号が空です。')
                else:
                    row_errors.append(f'行{row_num}: 口座番号が無効です（7桁の数字である必要があります）: {account_number_value}')
            
            # 振込金額
            transfer_amount = row.get('transfer_amount')
            if pd.isna(transfer_amount):
                row_errors.append(f'行{row_num}: 振込金額が空です。')
            else:
                try:
                    transfer_amount = int(float(transfer_amount))
                    if transfer_amount < 0:
                        row_errors.append(f'行{row_num}: 振込金額は0以上である必要があります。')
                except (ValueError, TypeError):
                    row_errors.append(f'行{row_num}: 振込金額が無効です（数値である必要があります）。')
            
            if row_errors:
                errors.extend(row_errors)
            else:
                processed_data.append({
                    'customer_name': customer_name,
                    'bank_code': bank_code,
                    'branch_code': branch_code,
                    'account_type': account_type,
                    'account_number': account_number,
                    'transfer_amount': transfer_amount
                })
        
        if errors:
            return pd.DataFrame(), errors
        
        return pd.DataFrame(processed_data), []
    
    except Exception as e:
        errors.append(f'CSVファイルの読み込み中にエラーが発生しました: {str(e)}')
        return pd.DataFrame(), errors


def process_uploaded_file(file: FileStorage) -> Tuple[pd.DataFrame, List[str]]:
    """
    アップロードされたファイルを処理

    Args:
        file: アップロードされたファイル

    Returns:
        Tuple[pd.DataFrame, List[str]]: (データフレーム, エラーメッセージのリスト)
    """
    filename = file.filename.lower()
    
    if filename.endswith('.xlsx'):
        return process_excel_file(file)
    elif filename.endswith('.csv'):
        return process_csv_file(file)
    else:
        return pd.DataFrame(), ['サポートされていないファイル形式です。Excel (.xlsx) または CSV (.csv) ファイルをアップロードしてください。']

