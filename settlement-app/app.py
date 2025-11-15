# Flask関連のモジュールをインポート
from flask import Flask, request, redirect, render_template, send_from_directory, flash
import os  # ファイルパス操作やディレクトリ作成に使用
from werkzeug.utils import secure_filename  # ファイル名を安全な形式に変換（セキュリティ対策）

# Flaskアプリケーションのインスタンスを作成
# __name__は現在のモジュール名を表し、テンプレートや静的ファイルの場所を特定するために使用
app = Flask(__name__)
# flashメッセージを使用するためにシークレットキーを設定
# 本番環境では環境変数から取得することを推奨
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# アップロード先のディレクトリを設定
# os.path.join(): パスを結合（OSに依存しない安全な方法）
# os.path.dirname(): ファイルのディレクトリ部分を取得
# os.path.abspath(__file__): このファイルの絶対パスを取得
# 結果: このファイルと同じディレクトリにある "uploads" フォルダのパス
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
# Flaskアプリケーションの設定に保存（後で参照できるように）
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# アップロードファイルはエクセルのみ許可
ALLOWED_EXTENSIONS = {"xlsx", "xlsm"}


def allowed_file(filename):
    """
    ファイル名が許可された拡張子かどうかをチェックする関数

    Args:
        filename (str): チェックするファイル名

    Returns:
        bool: 許可された拡張子の場合はTrue、そうでなければFalse

    処理の流れ:
        1. ファイル名に "." が含まれているか確認（拡張子があるか）
        2. ファイル名を "." で分割し、最後の部分（拡張子）を取得
        3. 拡張子を小文字に変換して、許可リストと照合
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def upload_file():
    """
    ファイルアップロードを処理するルートハンドラー（複数ファイル対応）

    GETリクエスト: アップロードフォームを表示
    POSTリクエスト: アップロードされたファイルを保存
    """
    if request.method == "POST":
        # POSTリクエストの場合（ファイルが送信された場合）

        # ファイルがリクエストに存在するか確認
        # フォームに "file" という名前のフィールドがない場合はリダイレクト
        if "file" not in request.files:
            flash("ファイルが選択されていません", "error")
            return redirect(request.url)

        # リクエストから複数のファイルオブジェクトを取得
        # getlist()を使用することで、複数のファイルをリストとして取得
        files = request.files.getlist("file")

        # アップロード成功/失敗のカウンター
        uploaded_files = []
        failed_files = []

        # 各ファイルを処理
        for file in files:
            # ファイル名が空かチェック（ファイルが選択されていない場合）
            if file.filename == "":
                continue  # 空のファイルはスキップ

            # ファイルが存在し、かつ許可された拡張子かどうかをチェック
            if file and allowed_file(file.filename):
                try:
                    # ファイル名を安全な形式に変換
                    # 例: "test file.xlsx" → "test_file.xlsx"（スペースや特殊文字を処理）
                    filename = secure_filename(file.filename)

                    # ファイルをアップロードフォルダに保存
                    # os.path.join()でアップロードフォルダのパスとファイル名を結合
                    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                    uploaded_files.append(filename)
                except Exception:
                    # ファイル保存時にエラーが発生した場合
                    failed_files.append(file.filename)
            else:
                # 許可されていない拡張子の場合
                failed_files.append(file.filename)

        # アップロード結果をメッセージで通知
        if uploaded_files:
            success_msg = (
                f"{len(uploaded_files)}個のファイルがアップロードされました: " f"{', '.join(uploaded_files)}"
            )
            flash(success_msg, "success")
        if failed_files:
            error_msg = (
                f"{len(failed_files)}個のファイルのアップロードに失敗しました"
                f"（Excelファイルのみ許可）: {', '.join(failed_files)}"
            )
            flash(error_msg, "error")

        # アップロード後、フォームページにリダイレクト
        return redirect(request.url)

    # GETリクエストの場合、またはPOSTでエラーがあった場合
    # アップロードフォームを表示するHTMLテンプレートをレンダリング
    return render_template("upload.html")


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """
    アップロードされたファイルをクライアントに送信するルートハンドラー

    Args:
        filename (str): URLパラメータから取得したファイル名

    Returns:
        ファイルの内容（ブラウザで表示またはダウンロード）

    注意:
        send_from_directory()を使用することで、アップロードフォルダ外のファイルへの
        アクセスを防ぎ、セキュリティを確保しています
    """
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    """
    このファイルが直接実行された場合（python app.py）にのみ実行される処理

    開発サーバーを起動する前に、アップロードフォルダが存在することを確認します
    """
    # アップロード先のディレクトリが存在するか確認し、存在しない場合は作成する
    # これにより、アップロード時にエラーが発生することを防ぎます
    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])

    # 開発サーバーを起動
    # debug=True: デバッグモードを有効化（コード変更時に自動リロード、エラー詳細表示）
    app.run(debug=True)
