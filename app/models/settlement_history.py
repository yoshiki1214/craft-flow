"""
精算書発行履歴モデル

精算書の一括生成・ダウンロード履歴を管理する。
"""

from datetime import datetime
from app import db


class SettlementHistory(db.Model):
    """
    精算書発行履歴テーブル

    精算書の一括生成・ダウンロード履歴を保存する。

    Attributes:
        id: 主キー（自動採番）
        year: 精算対象年
        month: 精算対象月
        file_name: 生成されたファイル名
        file_path: ファイルの保存パス
        file_format: ファイル形式（excel/pdf）
        created_at: 発行日時（自動設定）
    """

    __tablename__ = "settlement_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.Integer, nullable=False, comment="精算対象年")
    month = db.Column(db.Integer, nullable=False, comment="精算対象月")
    file_name = db.Column(db.String(255), nullable=False, comment="ファイル名")
    file_path = db.Column(db.String(500), nullable=False, comment="ファイル保存パス")
    file_format = db.Column(db.String(10), nullable=False, default="excel", comment="ファイル形式")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, comment="発行日時")

    # インデックスの定義
    __table_args__ = (
        db.Index("idx_settlement_history_year_month", "year", "month"),
        db.Index("idx_settlement_history_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        """オブジェクトの文字列表現を返す"""
        return f"<SettlementHistory {self.id}: {self.year}年{self.month}月 - {self.file_name}>"

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "id": self.id,
            "year": self.year,
            "month": self.month,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "file_format": self.file_format,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


