"""
全銀フォーマット変換機能

全銀フォーマット（全銀協標準フォーマット）への変換処理を行う。
"""

from flask import Blueprint, render_template

bank_format_bp = Blueprint("bank_format", __name__, url_prefix="/bank-format")


@bank_format_bp.route("/")
def index():
    """
    全銀フォーマット変換のトップページ

    Returns:
        トップページのHTML
    """
    return render_template("bank_format/index.html")
