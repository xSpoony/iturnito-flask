from ..extensions import db

class ConfiguracionHorario(db.Model):
    __tablename__ = 'configuracion_horarios'

    id = db.Column(db.Integer, primary_key=True)
    duracion_turno = db.Column(db.Integer, default=30)
    modalidad = db.Column(db.String(50), default='presencial')
    precio_consulta = db.Column(db.Float, default=0.0)

    # Clave Externa (ForeignKey) para la relación 1-a-1 con Doctor
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctores.id'), nullable=False, unique=True)

    # Relación 1-a-1 con Doctor
    # La propiedad 'configuracion' se define en el modelo Doctor
    doctor = db.relationship('Doctor', back_populates='configuracion')

    def to_dict(self):
        return {
            'duracion_turno': self.duracion_turno,
            'modalidad': self.modalidad,
            'precio_consulta': self.precio_consulta
        }

    def __repr__(self):
        return f'<ConfiguracionHorario Dr. {self.doctor_id}>'

