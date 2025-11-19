from app.extensions import db
import datetime

class Turno(db.Model):
    __tablename__ = 'turnos'

    id = db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='pendiente') # cambiado de 'reservado' a 'pendiente'
    modalidad = db.Column(db.String(50), default='presencial')
    observaciones = db.Column(db.Text, nullable=True)  # Notas del paciente al reservar
    notas_doctor = db.Column(db.Text, nullable=True)   # Notas del médico

    # --- Claves Externas ---
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctores.id'), nullable=False)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)

    # --- Relaciones (Muchos-a-1) ---
    doctor = db.relationship('Doctor', back_populates='turnos')
    paciente = db.relationship('Paciente', back_populates='turnos')

    def __repr__(self):
        return f'<Turno {self.id} - {self.fecha_hora} - {self.estado}>'

