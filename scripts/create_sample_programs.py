"""
体験プログラムの初期データを作成するスクリプト
"""

from app import create_app, db
from app.models import ExperienceProgram


def create_sample_programs():
    """サンプルの体験プログラムを作成する"""
    app = create_app()

    with app.app_context():
        # 既存のプログラムを確認
        existing = ExperienceProgram.query.count()
        if existing > 0:
            print(f"既に{existing}件のプログラムが登録されています。")
            response = input("削除して再作成しますか？ (y/N): ")
            if response.lower() != "y":
                print("処理を中止しました。")
                return

            # 既存のプログラムを削除
            ExperienceProgram.query.delete()
            db.session.commit()
            print("既存のプログラムを削除しました。")

        # サンプルプログラムを作成
        programs = [
            {
                "name": "陶芸体験",
                "description": "伝統的な陶芸技法を学び、自分だけのオリジナル作品を作成できます。初心者の方でも丁寧に指導いたします。",
                "price": 3500,
                "capacity": 8,
            },
            {
                "name": "染物体験",
                "description": "自然の草木を使った本格的な染物体験。エコバッグやハンカチなど、お好きなものを染めることができます。",
                "price": 2800,
                "capacity": 10,
            },
            {
                "name": "木工体験",
                "description": "地元の木材を使った木工体験。カッティングボードや小物入れなど、実用的な作品を作ります。",
                "price": 4000,
                "capacity": 6,
            },
            {
                "name": "和紙作り体験",
                "description": "伝統的な和紙作りの技法を体験。原料から作る本格的な和紙作りをお楽しみいただけます。",
                "price": 3000,
                "capacity": 12,
            },
            {
                "name": "藍染め体験",
                "description": "天然藍を使った本格的な藍染め体験。Tシャツやトートバッグなど、お持ち込みも可能です。",
                "price": 4500,
                "capacity": 8,
            },
        ]

        for program_data in programs:
            program = ExperienceProgram(**program_data)
            db.session.add(program)

        db.session.commit()
        print(f"\n{len(programs)}件の体験プログラムを作成しました：")

        # 作成されたプログラムを表示
        all_programs = ExperienceProgram.query.all()
        for p in all_programs:
            print(f"  - {p.name} (定員: {p.capacity}名, 料金: ¥{p.price:,})")

        print("\n✅ 初期データの作成が完了しました！")


if __name__ == "__main__":
    create_sample_programs()
