from ..extensions import db, bcrypt
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='paciente') # admin, doctor, paciente
    telefono = db.Column(db.String(20), nullable=True)
    dni = db.Column(db.String(20), unique=True, nullable=True)

    # --- Relaciones (El "otro lado" del 1-a-1) ---
    paciente_perfil = db.relationship('Paciente', back_populates='user', uselist=False)
    doctor_perfil = db.relationship('Doctor', back_populates='user', uselist=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.name} ({self.rol})>'

