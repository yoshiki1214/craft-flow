# 全銀フォーマット変換システム

エクセル顧客情報を全銀フォーマットに変換するためのFlaskアプリケーションです。

## 機能概要

- 顧客データの管理・保存
- 全銀フォーマット変換に必要な顧客情報の管理
- 振込データの一括管理
- 振込履歴の管理

## データベース設計

### customers テーブル

顧客情報を格納するテーブルです。

| カラム名 | 型 | 制約 | 説明 |
|---------|-----|------|------|
| id | Integer | PRIMARY KEY | 主キー |
| customer_name | String(100) | NOT NULL | 顧客名 |
| bank_code | String(4) | NOT NULL | 銀行コード（4桁数字） |
| branch_code | String(3) | NOT NULL | 支店コード（3桁数字） |
| account_type | String(1) | NOT NULL | 口座種別（1: 普通, 2: 当座, 4: 貯蓄） |
| account_number | String(7) | NOT NULL | 口座番号（7桁数字） |
| transfer_amount | Integer | NOT NULL | 振込金額（0以上） |
| created_at | DateTime | NOT NULL | 登録日時 |
| updated_at | DateTime | NOT NULL | 更新日時 |

### transfer_history テーブル

振込履歴を格納するテーブルです。

| カラム名 | 型 | 制約 | 説明 |
|---------|-----|------|------|
| id | Integer | PRIMARY KEY | 主キー |
| file_name | String(255) | NOT NULL | ファイル名 |
| record_count | Integer | NOT NULL | 件数（0以上） |
| created_at | DateTime | NOT NULL | 作成日時 |

## 環境構築

### 1. 仮想環境の作成

```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化（Windows）
venv\Scripts\activate

# 仮想環境の有効化（Mac/Linux）
source venv/bin/activate
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. データベースの初期化

```bash
# マイグレーションディレクトリの初期化
flask db init

# マイグレーションファイルの作成
flask db migrate -m "Initial migration: Create customers and transfer_history tables"

# データベースの作成（テーブル作成）
flask db upgrade
```

### 4. 開発サーバーの起動

```bash
flask run
```

## データベース設定

### 開発環境（SQLite）

デフォルトでSQLiteが使用されます。データベースファイルは `instance/app.db` に作成されます。

### 本番環境（PostgreSQL）

環境変数 `DATABASE_URL` を設定することで、PostgreSQLに切り替えることができます。

```bash
# .env ファイルに設定
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## バリデーション

### 顧客データのバリデーション

- **銀行コード**: 4桁の数字のみ
- **支店コード**: 3桁の数字のみ
- **口座種別**: 1, 2, 4 のいずれか
- **口座番号**: 7桁の数字のみ
- **振込金額**: 0以上の整数

### 使用例

```python
from app import db, create_app
from app.models import Customer

app = create_app()
with app.app_context():
    # 顧客データの作成
    customer = Customer(
        customer_name='テスト顧客',
        bank_code='0001',
        branch_code='001',
        account_type='1',
        account_number='1234567',
        transfer_amount=10000
    )
    
    # バリデーション
    errors = customer.validate()
    if errors:
        print(f'バリデーションエラー: {errors}')
    else:
        # データベースに保存
        db.session.add(customer)
        db.session.commit()
```

## マイグレーション

### マイグレーションファイルの作成

```bash
flask db migrate -m "マイグレーションメッセージ"
```

### マイグレーションの適用

```bash
flask db upgrade
```

### マイグレーションのロールバック

```bash
flask db downgrade
```

## セキュリティ

- データベース接続情報は環境変数で管理
- 顧客情報は暗号化保存を検討（将来実装予定）
- CSRF対策はFlask-WTFを使用（将来実装予定）

## 今後の拡張予定

- アップロード機能との連携（顧客データをDBに保存）
- 履歴画面から過去ファイルダウンロード機能
- 顧客情報の暗号化保存
- 大量データ対応の最適化

## ライセンス

このプロジェクトは内部使用のためのものです。

