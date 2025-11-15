"""
フォーム定義

ファイルアップロード用のフォームを定義します。
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField
from wtforms.validators import DataRequired


class CustomerUploadForm(FlaskForm):
    """
    顧客データアップロードフォーム

    Excel/CSVファイルをアップロードするためのフォームです。
    """

    file = FileField(
        '顧客データファイル',
        validators=[
            FileRequired(message='ファイルを選択してください。'),
            FileAllowed(['xlsx', 'csv'], message='Excel (.xlsx) または CSV (.csv) ファイルのみアップロードできます。')
        ],
        render_kw={'accept': '.xlsx,.csv'}
    )
    submit = SubmitField('アップロード')

