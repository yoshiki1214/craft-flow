"""
機能モジュール

6つの主要機能を管理する：
1. メインダッシュボード (main)
2. 認証機能 (auth)
3. 全銀フォーマット変換 (bank_format)
4. POS売上レポート (pos)
5. 精算書ファイル作成 (settlement)
6. 予約管理 (reservation)
7. ユーザー管理 (user_management)
"""

from flask import Flask


def register_features(app: Flask) -> None:
    """
    すべての機能Blueprintをアプリケーションに登録する

    Args:
        app: Flaskアプリケーションインスタンス
    """
    # メインダッシュボード
    from app.features import main

    app.register_blueprint(main.main_bp)

    # 認証機能
    from app.features import auth

    app.register_blueprint(auth.auth_bp)

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

    # ユーザー管理機能
    from app.features import user_management

    app.register_blueprint(user_management.user_management_bp)
