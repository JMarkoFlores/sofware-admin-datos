from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from models.base import Base


class Lector(Base):
    __tablename__ = 'lectores'

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo_estudiante = Column(String(20), unique=True, nullable=False)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    email = Column(String(100))
    telefono = Column(String(20))
    carrera = Column(String(100))
    facultad = Column(String(100))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'codigo_estudiante': self.codigo_estudiante,
            'nombres': self.nombres,
            'apellidos': self.apellidos,
            'email': self.email,
            'telefono': self.telefono,
            'carrera': self.carrera,
            'facultad': self.facultad,
            'activo': self.activo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
