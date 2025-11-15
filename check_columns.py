"""Excelファイルの列名を詳細に確認"""

import pandas as pd

df = pd.read_excel("C:/Users/fumif/Downloads/顧客管理データ_全銀フォーマット.xlsx", engine="openpyxl")

print("=== 実際の列名（詳細） ===")
for i, col in enumerate(df.columns, 1):
    print(f'{i}. "{col}" (repr: {repr(col)})')

print("\n=== 列名の正規化テスト ===")
# 列名の前後の空白を削除
df.columns = df.columns.str.strip()
print("正規化後:")
for i, col in enumerate(df.columns, 1):
    print(f'{i}. "{col}"')

print("\n=== マッピングテスト ===")
REQUIRED_COLUMNS = {
    "customer_name": ["顧客名", "customer_name", "顧客", "名前", "事業者名", "代表者氏名"],
    "bank_name": ["銀行名", "bank_name", "銀行", "金融機関名"],
    "bank_code": ["銀行コード", "bank_code", "銀行コード", "金融機関コード"],
    "branch_name": ["支店名", "branch_name", "支店"],
    "branch_code": ["支店コード", "branch_code", "支店コード"],
    "account_type": ["口座種別", "account_type", "口座タイプ", "種別", "預金種目"],
    "account_number": ["口座番号", "account_number", "口座", "番号"],
    "transfer_amount": ["振込金額", "transfer_amount", "金額", "振込", "金額"],
}

column_mapping = {}
for standard_name, possible_names in REQUIRED_COLUMNS.items():
    for col in df.columns:
        if col in possible_names:
            if col not in column_mapping:
                column_mapping[col] = standard_name
                print(f'マッピング: "{col}" -> {standard_name}')
            break

print("\n=== マッピング結果 ===")
for orig, mapped in column_mapping.items():
    print(f'"{orig}" -> {mapped}')

print("\n=== 見つからなかった列 ===")
for standard_name, possible_names in REQUIRED_COLUMNS.items():
    found = False
    for col in df.columns:
        if col in possible_names:
            found = True
            break
    if not found:
        print(f"{standard_name}: {possible_names}")
