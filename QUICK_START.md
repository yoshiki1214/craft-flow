# クイックスタートガイド

## エラーが発生した場合の対処法

### エラー: `ModuleNotFoundError: No module named 'flask_sqlalchemy'`

このエラーが発生する場合、以下の手順で解決できます：

#### 1. 仮想環境の確認

仮想環境を使用している場合、まず有効化してください：

```bash
# Windowsの場合
venv\Scripts\activate

# Mac/Linuxの場合
source venv/bin/activate
```

#### 2. パッケージの再インストール

```bash
pip install -r requirements.txt
```

#### 3. Python環境の確認

使用しているPython環境を確認：

```bash
python --version
which python  # Mac/Linux
where python  # Windows
```

#### 4. 直接インポートテスト

パッケージが正しくインストールされているか確認：

```bash
python -c "from flask_sqlalchemy import SQLAlchemy; print('OK')"
```

#### 5. アプリケーションの起動

```bash
python app.py
```

## 正常に起動した場合

以下のメッセージが表示されれば成功です：

```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

ブラウザで `http://localhost:5000/pos/` にアクセスしてください。

