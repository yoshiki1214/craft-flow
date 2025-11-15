"""
データベースモデル定義

全銀フォーマット変換に必要な顧客データを管理するためのモデルを定義します。
"""
from app import db
from datetime import datetime
from sqlalchemy import CheckConstraint, Index
import re


class Customer(db.Model):
    """
    顧客情報テーブル
    
    全銀フォーマット変換に必要な顧客データを格納します。
    """
    __tablename__ = 'customers'
    
    # 主キー
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 顧客名（必須）
    customer_name = db.Column(db.String(100), nullable=False, comment='顧客名')
    
    # 銀行コード（4桁固定、必須）
    bank_code = db.Column(db.String(4), nullable=False, comment='銀行コード')
    
    # 支店コード（3桁固定、必須）
    branch_code = db.Column(db.String(3), nullable=False, comment='支店コード')
    
    # 口座種別（1桁固定、必須）
    # 1: 普通, 2: 当座, 4: 貯蓄
    account_type = db.Column(db.String(1), nullable=False, comment='口座種別')
    
    # 口座番号（7桁固定、必須）
    account_number = db.Column(db.String(7), nullable=False, comment='口座番号')
    
    # 振込金額（必須、0以上）
    transfer_amount = db.Column(db.Integer, nullable=False, comment='振込金額')
    
    # 登録日時（自動設定）
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment='登録日時'
    )
    
    # 更新日時（自動更新）
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment='更新日時'
    )
    
    # テーブル制約
    __table_args__ = (
        # 銀行コードは4桁のみ許可（SQLite/PostgreSQL互換）
        CheckConstraint(
            "LENGTH(bank_code) = 4",
            name='check_bank_code_length'
        ),
        # 支店コードは3桁のみ許可
        CheckConstraint(
            "LENGTH(branch_code) = 3",
            name='check_branch_code_length'
        ),
        # 口座種別は1桁で1,2,4のみ許可
        CheckConstraint(
            "account_type IN ('1', '2', '4')",
            name='check_account_type'
        ),
        # 口座番号は7桁のみ許可
        CheckConstraint(
            "LENGTH(account_number) = 7",
            name='check_account_number_length'
        ),
        # 振込金額は0以上
        CheckConstraint(
            'transfer_amount >= 0',
            name='check_transfer_amount_positive'
        ),
        # インデックス（検索パフォーマンス向上）
        Index('idx_customer_name', 'customer_name'),
        Index('idx_bank_branch', 'bank_code', 'branch_code'),
        Index('idx_created_at', 'created_at'),
    )
    
    @staticmethod
    def validate_bank_code(bank_code: str) -> bool:
        """
        銀行コードの形式を検証
        
        Args:
            bank_code: 銀行コード（4桁数字）
        
        Returns:
            bool: 有効な場合True
        """
        return bool(re.match(r'^\d{4}$', bank_code))
    
    @staticmethod
    def validate_branch_code(branch_code: str) -> bool:
        """
        支店コードの形式を検証
        
        Args:
            branch_code: 支店コード（3桁数字）
        
        Returns:
            bool: 有効な場合True
        """
        return bool(re.match(r'^\d{3}$', branch_code))
    
    @staticmethod
    def validate_account_type(account_type: str) -> bool:
        """
        口座種別の形式を検証
        
        Args:
            account_type: 口座種別（1, 2, 4のいずれか）
        
        Returns:
            bool: 有効な場合True
        """
        return account_type in ('1', '2', '4')
    
    @staticmethod
    def validate_account_number(account_number: str) -> bool:
        """
        口座番号の形式を検証
        
        Args:
            account_number: 口座番号（7桁数字）
        
        Returns:
            bool: 有効な場合True
        """
        return bool(re.match(r'^\d{7}$', account_number))
    
    def validate(self) -> list:
        """
        モデルのバリデーションを実行
        
        Returns:
            list: エラーメッセージのリスト（空の場合は正常）
        """
        errors = []
        
        if not self.validate_bank_code(self.bank_code):
            errors.append(f'銀行コードは4桁の数字である必要があります: {self.bank_code}')
        
        if not self.validate_branch_code(self.branch_code):
            errors.append(f'支店コードは3桁の数字である必要があります: {self.branch_code}')
        
        if not self.validate_account_type(self.account_type):
            errors.append(f'口座種別は1, 2, 4のいずれかである必要があります: {self.account_type}')
        
        if not self.validate_account_number(self.account_number):
            errors.append(f'口座番号は7桁の数字である必要があります: {self.account_number}')
        
        if self.transfer_amount < 0:
            errors.append(f'振込金額は0以上である必要があります: {self.transfer_amount}')
        
        return errors
    
    def __repr__(self) -> str:
        """
        オブジェクトの文字列表現を返す
        
        Returns:
            str: 顧客情報の文字列表現
        """
        return f'<Customer {self.id}: {self.customer_name}>'
    
    def to_dict(self) -> dict:
        """
        顧客情報を辞書形式に変換
        
        Returns:
            dict: 顧客情報の辞書
        """
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'bank_code': self.bank_code,
            'branch_code': self.branch_code,
            'account_type': self.account_type,
            'account_number': self.account_number,
            'transfer_amount': self.transfer_amount,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class TransferHistory(db.Model):
    """
    振込履歴テーブル
    
    全銀フォーマット変換処理の履歴を管理します。
    """
    __tablename__ = 'transfer_history'
    
    # 主キー
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # ファイル名（必須）
    file_name = db.Column(db.String(255), nullable=False, comment='ファイル名')
    
    # 件数（必須、0以上）
    record_count = db.Column(db.Integer, nullable=False, comment='件数')
    
    # 作成日時（自動設定）
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment='作成日時'
    )
    
    # テーブル制約
    __table_args__ = (
        # 件数は0以上
        CheckConstraint(
            'record_count >= 0',
            name='check_record_count_positive'
        ),
        # インデックス（検索パフォーマンス向上）
        Index('idx_file_name', 'file_name'),
        Index('idx_created_at', 'created_at'),
    )
    
    def __repr__(self) -> str:
        """
        オブジェクトの文字列表現を返す
        
        Returns:
            str: 振込履歴の文字列表現
        """
        return f'<TransferHistory {self.id}: {self.file_name}>'
    
    def to_dict(self) -> dict:
        """
        振込履歴を辞書形式に変換
        
        Returns:
            dict: 振込履歴の辞書
        """
        return {
            'id': self.id,
            'file_name': self.file_name,
            'record_count': self.record_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

