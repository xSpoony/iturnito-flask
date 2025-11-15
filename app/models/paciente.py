from ..extensions import db

class Paciente(db.Model):
    __tablename__ = 'pacientes'

    id = db.Column(db.Integer, primary_key=True)
    obra_social = db.Column(db.String(100))

    # --- Clave Externa (ForeignKey) para la relación 1-a-1 con User ---
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    # --- Relaciones ---
    # Define la relación 1-a-1 con User
    user = db.relationship('User', back_populates='paciente_perfil')

    # Define la relación 1-a-Muchos con Turno
    turnos = db.relationship('Turno', back_populates='paciente', lazy=True)

    def __repr__(self):
        return f'<Paciente {self.user.name if self.user else self.id}>'
