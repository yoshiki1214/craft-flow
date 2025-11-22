"""
日次売上集計データモデル

pos_salesテーブルのデータを日別・商品別で集計した結果を保存するテーブル。
"""

from datetime import datetime
from app import db


class DailySales(db.Model):
    """
    日次売上集計データテーブル

    pos_salesテーブルのデータを日別で集計した結果を保存する。
    Excelファイルへ出力する際の集計元データとなる。

    同営業日の別集計ファイル（POSレジの打ち間違え訂正等）も保存可能。

    Attributes:
        id: 主キー（自動採番）
        sale_date: 売上日 (YYYY-MM-DD)
        total_sales_amount: 日次合計売上
        created_at: 集計日時（自動設定）

    Indexes:
        idx_daily_sales_date_created: sale_dateとcreated_atの複合インデックス
    """

    __tablename__ = "daily_sales"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sale_date = db.Column(db.String, nullable=False, comment="売上日 (YYYY-MM-DD)")
    total_sales_amount = db.Column(db.Integer, nullable=False, comment="日次合計売上")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, comment="集計日時")

    # 複合インデックスの定義
    # sale_dateで検索し、created_atでソートするクエリを高速化
    __table_args__ = (db.Index("idx_daily_sales_date_created", "sale_date", "created_at"),)

    def __repr__(self) -> str:
        """オブジェクトの文字列表現を返す"""
        return f"<DailySales {self.sale_date}: {self.total_sales_amount}>"
