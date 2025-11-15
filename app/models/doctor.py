from ..extensions import db

class Doctor(db.Model):
    __tablename__ = 'doctores'

    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(50), unique=True)

    # --- Claves Externas (ForeignKeys) ---
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    especialidad_id = db.Column(db.Integer, db.ForeignKey('especialidades.id'), nullable=True)

    # --- Relaciones ---
    # Relación 1-a-1 con User
    user = db.relationship('User', back_populates='doctor_perfil')

    # Relación Muchos-a-1 con Especialidad
    especialidad = db.relationship('Especialidad', back_populates='doctores')

    # Relación 1-a-Muchos con Turno
    turnos = db.relationship('Turno', back_populates='doctor', lazy=True)

    # Relación 1-a-Muchos con HorarioDisponible
    horarios_disponibles = db.relationship('HorarioDisponible', back_populates='doctor', lazy=True, cascade="all, delete-orphan")

    # Relación 1-a-1 con ConfiguracionHorario
    configuracion = db.relationship('ConfiguracionHorario', back_populates='doctor', uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Doctor {self.user.name if self.user else self.id}>'

