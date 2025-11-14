# Craft Flow

POS売上データ管理システム

## 機能概要

Craft Flowは以下の4つの機能で構成されています：

1. **全銀フォーマット変換** (`/bank-format/`)
2. **POS売上レポート** (`/pos/`) - 実装済み
3. **精算書ファイル作成** (`/settlement/`)
4. **予約管理** (`/reservation/`)

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. データベースの初期化

```bash
# マイグレーションの初期化（初回のみ）
flask db init

# マイグレーションファイルの作成
flask db migrate -m "Initial migration"

# データベースの作成
flask db upgrade
```

### 3. アプリケーションの起動

```bash
python app.py
```

ブラウザで `http://localhost:5000` にアクセスしてください。

## テストの実行

### すべてのテストを実行

```bash
pytest
```

### POS機能のテストのみ実行

```bash
pytest tests/test_pos_features.py
```

### カバレッジレポート付きで実行

```bash
pytest --cov=app --cov-report=html
```

カバレッジレポートは `htmlcov/index.html` に生成されます。

## POS機能の使用方法

### 1. ダッシュボードにアクセス

ブラウザで `http://localhost:5000/pos/` にアクセスします。

### 2. PDFファイルのアップロード

1. 「PDFファイルをアップロード」をクリック
2. POS売上レポートのPDFファイルを選択（複数選択可）
3. 必要に応じて「上書きオプション」をチェック
   - チェック時: 営業日とレジ番号が同じデータが存在し、出力日時が新しい場合に上書き
   - チェックなし: 重複データはスキップ
4. 「アップロード」をクリック

### 3. 処理結果の確認

ダッシュボードに以下の情報が表示されます：
- 総レコード数
- 営業日数
- POSレジ数

## プロジェクト構造

```
craft-flow/
├── app/
│   ├── __init__.py          # Application Factory
│   ├── features/             # 機能モジュール
│   │   ├── __init__.py      # 機能登録関数
│   │   ├── bank_format.py   # 全銀フォーマット変換
│   │   ├── pos.py           # POS売上レポート
│   │   ├── settlement.py    # 精算書ファイル作成
│   │   └── reservation.py  # 予約管理
│   ├── models/              # データベースモデル
│   ├── templates/           # Jinja2テンプレート
│   └── utils/               # ユーティリティ関数
├── tests/                   # テストファイル
├── migrations/              # データベースマイグレーション
├── instance/                # インスタンスファイル（DB等）
├── app.py                   # エントリーポイント
└── requirements.txt        # 依存関係
```

## 開発ガイドライン

### 新機能の追加

1. `app/features/` に新しい機能ファイルを作成
2. Blueprintを定義
3. `app/features/__init__.py` の `register_features()` 関数に登録

### テストの追加

1. `tests/` ディレクトリにテストファイルを作成
2. `test_*.py` の命名規則に従う
3. `pytest` で実行して動作確認

## トラブルシューティング

### データベースエラー

```bash
# データベースをリセットする場合
rm instance/app.db
flask db upgrade
```

### テストが失敗する場合

```bash
# テスト環境をクリーンアップ
pytest --cache-clear
```

## ライセンス

このプロジェクトは内部使用を目的としています。

