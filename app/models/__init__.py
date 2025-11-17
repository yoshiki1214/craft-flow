"""
<<<<<<< HEAD
データベースモデルの初期化

すべてのモデルをインポートして、Flask-SQLAlchemyに認識させる
循環インポートを防ぐため、dbはappからインポート
"""
from app import db
from app.models.reservation import Program, Reservation

__all__ = ['db', 'Program', 'Reservation']
=======
データベースモデルモジュール

すべてのデータベースモデルをインポートして、Flask-Migrateが認識できるようにする。
"""

from app.models.pos_sales import PosSales
from app.models.daily_sales import DailySales

__all__ = ["PosSales", "DailySales"]
>>>>>>> 0ba6c74c70245a273989b3356430507d4923e121
