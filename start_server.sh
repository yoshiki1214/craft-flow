#!/bin/bash

# 既存のFlaskサーバーを停止
echo "既存のFlaskプロセスを検索..."
pkill -f "flask run" 2>/dev/null || echo "停止するプロセスはありません"
pkill -f "python.*app.py" 2>/dev/null || echo "停止するプロセスはありません"
sleep 1

# 仮想環境をアクティベート
source .venv/bin/activate

# Flaskサーバーを起動
echo "Flaskサーバーを起動します..."
echo "アクセスURL: http://127.0.0.1:5000/settlement/upload"
echo "停止するには Ctrl+C を押してください"
echo ""

export FLASK_APP=app.py
export FLASK_DEBUG=True
flask run
