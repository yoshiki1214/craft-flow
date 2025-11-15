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


@app.route("/", methods=["GET"])
def index():
    """
    アップロードフォームを表示するルートハンドラー

    Returns:
        アップロードフォームのHTMLテンプレート
    """
    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
def upload_files():
    """
    顧客データと委託販売売上データのファイルアップロードを一括処理するルートハンドラー

    Returns:
        アップロード結果をフラッシュメッセージで表示し、フォームページにリダイレクト
    """
    # 顧客データの処理
    if "customer_file" in request.files:
        customer_file = request.files["customer_file"]
        if customer_file.filename != "":
            if customer_file and allowed_file(customer_file.filename):
                try:
                    customers_folder = os.path.join(app.config["UPLOAD_FOLDER"], "customers")
                    if not os.path.exists(customers_folder):
                        os.makedirs(customers_folder)
                    filename = secure_filename(customer_file.filename)
                    customer_file.save(os.path.join(customers_folder, filename))
                    flash(f"顧客データ: {filename} がアップロードされました", "success")
                except Exception:
                    flash(f"顧客データ: {customer_file.filename} のアップロードに失敗しました", "error")
            else:
                flash(
                    f"顧客データ: {customer_file.filename} は許可されていないファイル形式です（Excelファイルのみ許可）",
                    "error",
                )

    # 委託販売売上データの処理
    if "sales_file" in request.files:
        sales_file = request.files["sales_file"]
        if sales_file.filename != "":
            if sales_file and allowed_file(sales_file.filename):
                try:
                    sales_folder = os.path.join(app.config["UPLOAD_FOLDER"], "sales")
                    if not os.path.exists(sales_folder):
                        os.makedirs(sales_folder)
                    filename = secure_filename(sales_file.filename)
                    sales_file.save(os.path.join(sales_folder, filename))
                    flash(f"委託販売売上データ: {filename} がアップロードされました", "success")
                except Exception:
                    flash(f"委託販売売上データ: {sales_file.filename} のアップロードに失敗しました", "error")
            else:
                flash(
                    f"委託販売売上データ: {sales_file.filename} は許可されていないファイル形式です（Excelファイルのみ許可）",
                    "error",
                )

    # どちらのファイルも選択されていない場合
    customer_selected = "customer_file" in request.files and request.files["customer_file"].filename != ""
    sales_selected = "sales_file" in request.files and request.files["sales_file"].filename != ""
    if not customer_selected and not sales_selected:
        flash("少なくとも1つのファイルを選択してください", "error")

    return redirect("/")


@app.route("/upload/customers", methods=["POST"])
def upload_customers():
    """
    顧客データのファイルアップロードを処理するルートハンドラー（1ファイル対応）

    Returns:
        アップロード結果をフラッシュメッセージで表示し、フォームページにリダイレクト
    """
    # ファイルがリクエストに存在するか確認
    if "file" not in request.files:
        flash("ファイルが選択されていません", "error")
        return redirect("/")

    file = request.files["file"]

    # ファイル名が空かチェック
    if file.filename == "":
        flash("ファイルが選択されていません", "error")
        return redirect("/")

    # 顧客データ用のサブディレクトリ
    customers_folder = os.path.join(app.config["UPLOAD_FOLDER"], "customers")
    if not os.path.exists(customers_folder):
        os.makedirs(customers_folder)

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file.save(os.path.join(customers_folder, filename))
            flash(f"顧客データ: {filename} がアップロードされました", "success")
        except Exception:
            flash(f"顧客データ: {file.filename} のアップロードに失敗しました", "error")
    else:
        flash(
            f"顧客データ: {file.filename} は許可されていないファイル形式です（Excelファイルのみ許可）",
            "error",
        )

    return redirect("/")


@app.route("/upload/sales", methods=["POST"])
def upload_sales():
    """
    委託販売売上データのファイルアップロードを処理するルートハンドラー（1ファイル対応）

    Returns:
        アップロード結果をフラッシュメッセージで表示し、フォームページにリダイレクト
    """
    # ファイルがリクエストに存在するか確認
    if "file" not in request.files:
        flash("ファイルが選択されていません", "error")
        return redirect("/")

    file = request.files["file"]

    # ファイル名が空かチェック
    if file.filename == "":
        flash("ファイルが選択されていません", "error")
        return redirect("/")

    # 委託販売売上データ用のサブディレクトリ
    sales_folder = os.path.join(app.config["UPLOAD_FOLDER"], "sales")
    if not os.path.exists(sales_folder):
        os.makedirs(sales_folder)

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file.save(os.path.join(sales_folder, filename))
            flash(f"委託販売売上データ: {filename} がアップロードされました", "success")
        except Exception:
            flash(f"委託販売売上データ: {file.filename} のアップロードに失敗しました", "error")
    else:
        flash(
            f"委託販売売上データ: {file.filename} は許可されていないファイル形式です（Excelファイルのみ許可）",
            "error",
        )

    return redirect("/")


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
