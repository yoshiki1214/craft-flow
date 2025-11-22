"""
体験プログラムモデル
"""
from app import db


class ExperienceProgram(db.Model):
    """体験プログラムモデル"""
    
    __tablename__ = 'experience_programs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<ExperienceProgram {self.name}>'


