"""
機能モジュール

4つの主要機能を管理する：
1. 全銀フォーマット変換 (bank_format)
2. POS売上レポート (pos)
3. 精算書ファイル作成 (settlement)
4. 予約管理 (reservation)
"""

from flask import Flask


def register_features(app: Flask) -> None:
    """
    すべての機能Blueprintをアプリケーションに登録する

    Args:
        app: Flaskアプリケーションインスタンス
    """
    # 全銀フォーマット変換機能
    from app.features import bank_format

    app.register_blueprint(bank_format.bank_format_bp)

    # POS売上レポート機能
    from app.features import pos

    app.register_blueprint(pos.pos_bp)

    # 精算書ファイル作成機能
    from app.features import settlement

    app.register_blueprint(settlement.settlement_bp)

    # 予約管理機能
    from app.features import reservation

    app.register_blueprint(reservation.reservation_bp)
