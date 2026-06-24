from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from models.base import Base


class Autor(Base):
    __tablename__ = 'autores'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    nacionalidad = Column(String(50))
    fecha_nacimiento = Column(DateTime)
    biografia = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'nacionalidad': self.nacionalidad,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'biografia': self.biografia,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
