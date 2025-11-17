from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, NumberRange


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

    def __init__(self, *args, **kwargs):
        super(ReservationForm, self).__init__(*args, **kwargs)
        # フォームフィールドにTailwind CSSクラスを適用
        for field in self._fields.values():
            if field.type not in ['SubmitField', 'CSRFTokenField']:
                field.render_kw = {'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}
        
