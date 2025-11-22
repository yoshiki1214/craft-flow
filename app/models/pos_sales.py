"""
POS売上データモデル

PDFから抽出した明細レベルの生データを保存するテーブル。
"""

from datetime import datetime
from app import db


class PosSales(db.Model):
    """
    POS売上データテーブル

    PDFから抽出した明細レベルの生データをそのまま保存する。
    データの重複読み込み防止や、詳細な分析が必要な場合の元データとして機能する。

    Attributes:
        id: 主キー（自動採番）
        pos_number: POSレジ番号
        sale_date: 売上日 (YYYY-MM-DD)
        reported_at: 売上レポート作成日時 (YYYY-MM-DD-HH-SS)
        product_code: 商品コード
        product_name: 商品名
        quantity: 数量
        unit_price: 単価
        subtotal: 合計金額 (数量 * 単価)
        total_amount: POSレジ総合計金額
        pdf_source_file: 読み込み元PDFファイル名
        registration_date: 登録日時（自動設定）

    Indexes:
        idx_pos_sales_date: sale_date、pos_number、product_codeの複合インデックス
    """

    __tablename__ = "pos_sales"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pos_number = db.Column(db.String, nullable=False, comment="POSレジ番号")
    sale_date = db.Column(db.String, nullable=False, comment="売上日 (YYYY-MM-DD)")
    reported_at = db.Column(db.String, nullable=False, comment="売上レポート作成日時(YYYY-MM-DD-HH-SS)")
    product_code = db.Column(db.String, nullable=False, comment="商品コード")
    product_name = db.Column(db.String, nullable=False, comment="商品名")
    quantity = db.Column(db.Integer, nullable=False, comment="数量")
    unit_price = db.Column(db.Integer, nullable=False, comment="単価")
    subtotal = db.Column(db.Integer, nullable=False, comment="合計金額 (数量 * 単価)")
    total_amount = db.Column(db.Integer, nullable=False, comment="POSレジ総合計金額")
    pdf_source_file = db.Column(db.String, nullable=True, comment="読み込み元PDFファイル名")
    registration_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, comment="登録日時")

    # インデックスの定義（データ量が多い場合に備える）
    __table_args__ = (db.Index("idx_pos_sales_date", "sale_date", "pos_number", "product_code"),)

    def __repr__(self) -> str:
        """オブジェクトの文字列表現を返す"""
        return f"<PosSales {self.id}: {self.product_name} on {self.sale_date}>"
