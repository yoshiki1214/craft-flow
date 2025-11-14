"""
データベースモデルモジュール

すべてのデータベースモデルをインポートして、Flask-Migrateが認識できるようにする。
"""

from app.models.pos_sales import PosSales
from app.models.daily_sales import DailySales

__all__ = ["PosSales", "DailySales"]
