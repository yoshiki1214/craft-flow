from . import db

class ExperienceProgram(db.Model):
    __tablename__ = 'experience_programs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<ExperienceProgram {self.name}>'

class Reservation(db.Model):
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
