"""
予約モデル
"""
from app import db


class Reservation(db.Model):
    """予約モデル"""
    
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('experience_programs.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    reservation_date = db.Column(db.Date, nullable=False)
    number_of_participants = db.Column(db.Integer, nullable=False)

    program = db.relationship('ExperienceProgram', backref=db.backref('reservations', lazy=True, cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<Reservation {self.name} for program_id={self.program_id}>'


