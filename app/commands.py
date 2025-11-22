"""
Flaskカスタムコマンド定義モジュール
"""
import click
from flask.cli import with_appcontext


@click.command("seed")
@with_appcontext
def seed_command():
    """データベースに初期データを投入します。"""

    # コマンド実行時にモデルとdbをインポート
    from .models import ExperienceProgram
    from . import db

    programs_to_seed = [
        {
            "name": "藍染め体験 ハンカチ",
            "description": "天然藍を使った染色体験です。自分だけのオリジナルハンカチを染め上げます。",
            "price": 2000,
            "capacity": 15,
        },
        {
            "name": "天然藍を使った染色体験",
            "description": "Tシャツやストールなど、持ち込んだものを天然藍で染める本格的な体験です。",
            "price": 4600,
            "capacity": 10,
        },
    ]

    for program_data in programs_to_seed:
        # 同じ名前のプログラムが既に存在しないか確認
        if not ExperienceProgram.query.filter_by(name=program_data["name"]).first():
            program = ExperienceProgram(**program_data)
            db.session.add(program)
            click.echo(f"プログラム '{program.name}' を作成しました。")

    db.session.commit()
    click.echo("データベースの初期データ投入が完了しました。")


def init_app(app):
    """
    Flaskアプリケーションにカスタムコマンドを登録します。
    """
    app.cli.add_command(seed_command)
