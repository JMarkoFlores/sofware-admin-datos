from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from models.base import Base


class Auditoria(Base):
    __tablename__ = 'auditoria'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo_operacion = Column(String(50), nullable=False)
    modulo = Column(String(50), nullable=False)
    descripcion = Column(Text)
    usuario = Column(String(100))
    resultado = Column(String(20))
    fecha_hora = Column(DateTime, server_default=func.now())
    detalle = Column(Text)

    def to_dict(self):
        return {
            'id': self.id,
            'tipo_operacion': self.tipo_operacion,
            'modulo': self.modulo,
            'descripcion': self.descripcion,
            'usuario': self.usuario,
            'resultado': self.resultado,
            'fecha_hora': self.fecha_hora.isoformat() if self.fecha_hora else None,
            'detalle': self.detalle,
        }
