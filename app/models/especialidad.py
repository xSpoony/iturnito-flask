from ..extensions import db

class Especialidad(db.Model):
    __tablename__ = 'especialidades'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)

    # --- Relación (El "otro lado" del 1-a-Muchos) ---
    doctores = db.relationship('Doctor', back_populates='especialidad', lazy=True)

    def __repr__(self):
        return f'<Especialidad {self.nombre}>'
