"""
フォーム定義モジュール

Flask-WTFを使用してフォームクラスを定義
"""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, SelectField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError
from datetime import date


class ReservationForm(FlaskForm):
    """予約フォーム"""
    
    program_id = SelectField(
        '体験プログラム',
        coerce=int,
        validators=[DataRequired(message='体験プログラムを選択してください')],
        render_kw={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}
    )
    
    name = StringField(
        'お名前',
        validators=[
            DataRequired(message='お名前を入力してください'),
            Length(max=100, message='お名前は100文字以内で入力してください')
        ],
        render_kw={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
            'placeholder': '山田 太郎'
        }
    )
    
    email = StringField(
        'メールアドレス',
        validators=[
            DataRequired(message='メールアドレスを入力してください'),
            Email(message='有効なメールアドレスを入力してください'),
            Length(max=120, message='メールアドレスは120文字以内で入力してください')
        ],
        render_kw={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
            'placeholder': 'example@example.com',
            'type': 'email'
        }
    )
    
    phone_number = StringField(
        '電話番号',
        validators=[
            DataRequired(message='電話番号を入力してください'),
            Length(max=20, message='電話番号は20文字以内で入力してください')
        ],
        render_kw={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
            'placeholder': '090-1234-5678'
        }
    )
    
    reservation_date = DateField(
        '予約日',
        validators=[DataRequired(message='予約日を選択してください')],
        render_kw={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
            'type': 'date'
        }
    )
    
    number_of_participants = IntegerField(
        '参加人数',
        validators=[
            DataRequired(message='参加人数を入力してください'),
            NumberRange(min=1, max=100, message='参加人数は1〜100名で入力してください')
        ],
        render_kw={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
            'placeholder': '1',
            'type': 'number',
            'min': '1',
            'max': '100'
        }
    )
    
    def validate_reservation_date(self, field):
        """予約日のバリデーション（過去の日付は不可）"""
        if field.data and field.data < date.today():
            raise ValidationError('予約日は今日以降の日付を選択してください')
    
    def validate_number_of_participants(self, field):
        """参加人数のバリデーション（プログラムの定員を超えないか）"""
        # このバリデーションはコントローラ側で実装するため、ここでは簡易チェックのみ
        if field.data and field.data < 1:
            raise ValidationError('参加人数は1名以上で入力してください')

