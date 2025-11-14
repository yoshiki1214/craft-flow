"""
POS機能のテスト

POS機能のユニットテストと統合テストを含む。
"""

import os
import tempfile
from pathlib import Path
import pytest
from app import db
from app.models.pos_sales import PosSales
from app.features.pos import allowed_file, save_pdf_data_to_db


class TestPosFeatures:
    """POS機能のテストクラス"""

    def test_allowed_file_with_pdf(self):
        """PDFファイルが許可されていることを確認"""
        assert allowed_file("test.pdf") is True
        assert allowed_file("test.PDF") is True
        assert allowed_file("test.Pdf") is True

    def test_allowed_file_with_non_pdf(self):
        """PDF以外のファイルが拒否されることを確認"""
        assert allowed_file("test.txt") is False
        assert allowed_file("test.jpg") is False
        assert allowed_file("test") is False
        assert allowed_file("") is False

    def test_save_pdf_data_to_db_new_record(self, app, sample_pos_data):
        """新規レコードの保存をテスト"""
        with app.app_context():
            sales_records = [sample_pos_data]
            stats = save_pdf_data_to_db(sales_records, "test.pdf", overwrite=False)

            assert stats["inserted"] == 1
            assert stats["skipped"] == 0
            assert stats["overwritten"] == 0

            # データベースに保存されたことを確認
            saved_record = PosSales.query.filter_by(pos_number="POS1", sale_date="2025-11-05").first()
            assert saved_record is not None
            assert saved_record.product_name == "テスト商品"
            assert saved_record.quantity == 2

    def test_save_pdf_data_to_db_duplicate_skip(self, app, sample_pos_data):
        """重複データのスキップをテスト"""
        with app.app_context():
            # 最初のレコードを保存
            sales_records = [sample_pos_data]
            save_pdf_data_to_db(sales_records, "test1.pdf", overwrite=False)

            # 同じデータを再度保存（上書きオプションなし）
            stats = save_pdf_data_to_db(sales_records, "test2.pdf", overwrite=False)

            assert stats["inserted"] == 0
            assert stats["skipped"] == 1
            assert stats["overwritten"] == 0

            # データベースに1件のみ存在することを確認
            count = PosSales.query.filter_by(pos_number="POS1", sale_date="2025-11-05").count()
            assert count == 1

    def test_save_pdf_data_to_db_overwrite_newer(self, app, sample_pos_data):
        """新しいデータで上書きをテスト"""
        with app.app_context():
            # 古いデータを保存
            old_data = sample_pos_data.copy()
            old_data["reported_at"] = "2025-11-06 10:00:00"
            save_pdf_data_to_db([old_data], "old.pdf", overwrite=False)

            # 新しいデータで上書き
            new_data = sample_pos_data.copy()
            new_data["reported_at"] = "2025-11-06 17:30:00"
            new_data["product_name"] = "更新された商品"
            stats = save_pdf_data_to_db([new_data], "new.pdf", overwrite=True)

            assert stats["inserted"] == 0
            assert stats["skipped"] == 0
            assert stats["overwritten"] == 1

            # データが更新されたことを確認
            saved_record = PosSales.query.filter_by(pos_number="POS1", sale_date="2025-11-05").first()
            assert saved_record.product_name == "更新された商品"
            assert saved_record.reported_at == "2025-11-06 17:30:00"

    def test_save_pdf_data_to_db_overwrite_older(self, app, sample_pos_data):
        """古いデータでの上書きがスキップされることをテスト"""
        with app.app_context():
            # 新しいデータを保存
            new_data = sample_pos_data.copy()
            new_data["reported_at"] = "2025-11-06 17:30:00"
            save_pdf_data_to_db([new_data], "new.pdf", overwrite=False)

            # 古いデータで上書きを試みる
            old_data = sample_pos_data.copy()
            old_data["reported_at"] = "2025-11-06 10:00:00"
            old_data["product_name"] = "古い商品"
            stats = save_pdf_data_to_db([old_data], "old.pdf", overwrite=True)

            assert stats["inserted"] == 0
            assert stats["skipped"] == 1
            assert stats["overwritten"] == 0

            # データが更新されていないことを確認
            saved_record = PosSales.query.filter_by(pos_number="POS1", sale_date="2025-11-05").first()
            assert saved_record.product_name == "テスト商品"
            assert saved_record.reported_at == "2025-11-06 17:30:00"

    def test_save_pdf_data_to_db_empty_records(self, app):
        """空のレコードリストをテスト"""
        with app.app_context():
            stats = save_pdf_data_to_db([], "test.pdf", overwrite=False)

            assert stats["inserted"] == 0
            assert stats["skipped"] == 0
            assert stats["overwritten"] == 0


class TestPosRoutes:
    """POS機能のルーティングテスト"""

    def test_dashboard_route(self, client):
        """ダッシュボードルートのテスト"""
        response = client.get("/pos/")
        assert response.status_code == 200
        # 日本語の文字列はエンコードして確認
        assert "POSデータ管理ダッシュボード".encode("utf-8") in response.data

    def test_upload_get_route(self, client):
        """アップロードフォームのGETリクエストテスト"""
        response = client.get("/pos/upload")
        assert response.status_code == 200
        # 日本語の文字列はエンコードして確認
        assert "PDFファイルアップロード".encode("utf-8") in response.data

    def test_upload_post_route_no_file(self, client):
        """ファイルなしのPOSTリクエストテスト"""
        response = client.post("/pos/upload", data={})
        assert response.status_code == 302  # リダイレクト
        # フラッシュメッセージを確認するには、follow_redirects=Trueが必要

    def test_upload_post_route_with_empty_file(self, client):
        """空のファイルのPOSTリクエストテスト"""
        response = client.post(
            "/pos/upload",
            data={"files": (None, "")},
            follow_redirects=True,
        )
        assert response.status_code == 200
        # エラーメッセージが表示されることを確認
        assert "ファイルが選択されていません".encode("utf-8") in response.data
