"""
予約機能関連のフォーム定義
"""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, NumberRange, ValidationError
from datetime import date


class ExperienceProgramForm(FlaskForm):
    """体験プログラムフォーム"""
    name = StringField('プログラム名', validators=[DataRequired(message='プログラム名を入力してください。')])
    description = TextAreaField('説明', validators=[DataRequired(message='説明を入力してください。')])
    price = IntegerField('価格', validators=[
        DataRequired(message='価格を入力してください。'),
        NumberRange(min=0, message='価格は0円以上で入力してください。')
    ])
    capacity = IntegerField('定員', validators=[
        DataRequired(message='定員を入力してください。'),
        NumberRange(min=1, message='定員は1名以上で入力してください。')
    ])
    submit = SubmitField('登録')

    def __init__(self, *args, **kwargs):
        super(ExperienceProgramForm, self).__init__(*args, **kwargs)
        # フォームフィールドにTailwind CSSクラスを適用
        for field in self._fields.values():
            if field.type not in ['SubmitField', 'CSRFTokenField']:
                field.render_kw = {'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}


class ReservationForm(FlaskForm):
    """予約フォーム"""
    program_id = SelectField('体験プログラム', coerce=int, validators=[DataRequired(message='プログラムを選択してください。')])
    name = StringField('お名前', validators=[DataRequired(message='お名前を入力してください。')])
    email = StringField('メールアドレス', validators=[DataRequired(message='メールアドレスを入力してください。'), Email(message='有効なメールアドレスを入力してください。')])
    phone_number = StringField('電話番号', validators=[DataRequired(message='電話番号を入力してください。')])
    reservation_date = DateField('予約日', format='%Y-%m-%d', validators=[DataRequired(message='予約日を選択してください。')])
    number_of_participants = IntegerField('参加人数', validators=[
        DataRequired(message='参加人数を入力してください。'),
        NumberRange(min=1, message='1名様以上でご予約ください。')
    ])
    submit = SubmitField('予約を確定する')
    
    def validate_reservation_date(self, field):
        """予約日が今日以降であることを確認"""
        if field.data and field.data < date.today():
            raise ValidationError('日程が過ぎているので予約の受付が出来ません。')

    def __init__(self, *args, **kwargs):
        super(ReservationForm, self).__init__(*args, **kwargs)
        # フォームフィールドにTailwind CSSクラスを適用
        for field in self._fields.values():
            if field.type not in ['SubmitField', 'CSRFTokenField']:
                field.render_kw = {'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}


