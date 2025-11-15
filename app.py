"""
Flaskアプリケーションエントリーポイント

このファイルからFlaskアプリケーションを起動します。
"""
from dotenv import load_dotenv
from app import create_app

# .flaskenvファイルを読み込む
load_dotenv()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

