from ..extensions import db
import datetime

class HorarioDisponible(db.Model):
    __tablename__ = 'horarios_disponibles'

    id = db.Column(db.Integer, primary_key=True)

    dia_semana = db.Column(db.Integer, nullable=False)

    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)

    # --- Clave Externa ---
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctores.id'), nullable=False)

    # --- Relación (Muchos-a-1) ---
    doctor = db.relationship('Doctor', back_populates='horarios_disponibles')

    def to_dict(self):
        return {
            'dia_semana': self.dia_semana,
            'hora_inicio': self.hora_inicio.strftime('%H:%M'),
            'hora_fin': self.hora_fin.strftime('%H:%M')
        }

    def __repr__(self):
        return f'<Horario DrID: {self.doctor_id} - Día: {self.dia_semana}>'

