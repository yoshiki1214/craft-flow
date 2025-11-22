# テストガイド

## テストの実行方法

### 基本的な実行

```bash
# すべてのテストを実行
pytest

# 詳細な出力で実行
pytest -v

# 特定のテストファイルのみ実行
pytest tests/test_pos_features.py

# 特定のテストクラスのみ実行
pytest tests/test_pos_features.py::TestPosFeatures

# 特定のテストメソッドのみ実行
pytest tests/test_pos_features.py::TestPosFeatures::test_allowed_file_with_pdf
```

### カバレッジレポート

```bash
# カバレッジレポートを生成
pytest --cov=app --cov-report=html

# カバレッジレポートを確認
# htmlcov/index.html をブラウザで開く
```

## テストの種類

### ユニットテスト

個別の関数やメソッドの動作をテストします。

- `test_allowed_file_with_pdf`: PDFファイルの許可チェック
- `test_save_pdf_data_to_db_new_record`: 新規レコードの保存
- `test_save_pdf_data_to_db_duplicate_skip`: 重複データのスキップ

### 統合テスト

複数のコンポーネントが連携して動作することをテストします。

- `test_dashboard_route`: ダッシュボードの表示
- `test_upload_get_route`: アップロードフォームの表示
- `test_upload_post_route_no_file`: ファイルなしのPOSTリクエスト

## テストフィクスチャ

### app

テスト用のFlaskアプリケーションインスタンスを提供します。
一時的なデータベースを使用します。

### client

テスト用のHTTPクライアントを提供します。
Flaskのテストクライアントを使用してHTTPリクエストを送信できます。

### sample_pos_data

サンプルのPOSデータを提供します。
テストで使用する標準的なデータ構造です。

## テストの追加方法

### 新しいテストケースの追加

```python
def test_new_feature(self, client):
    """新しい機能のテスト"""
    response = client.get("/pos/new-feature")
    assert response.status_code == 200
```

### テストマーカーの使用

```python
import pytest

@pytest.mark.slow
def test_slow_operation(self):
    """時間がかかるテスト"""
    # テストコード
    pass
```

マーカー付きテストのみ実行：
```bash
pytest -m slow
```

## ベストプラクティス

1. **テストは独立していること**: 各テストは他のテストに依存しないようにする
2. **明確なテスト名**: テスト名から何をテストしているか分かるようにする
3. **適切なアサーション**: 期待される結果を明確にアサートする
4. **テストデータの管理**: フィクスチャを使用してテストデータを管理する
5. **エラーケースのテスト**: 正常系だけでなく異常系もテストする

## トラブルシューティング

### テストが失敗する場合

1. エラーメッセージを確認
2. テスト環境が正しくセットアップされているか確認
3. データベースの状態を確認

### Windows環境での注意点

Windows環境では、SQLiteファイルの削除時にPermissionErrorが発生する場合があります。
`tests/conftest.py`でエラーハンドリングを実装していますが、問題が続く場合は手動で一時ファイルを削除してください。

