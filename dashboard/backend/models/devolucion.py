from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base


class Devolucion(Base):
    __tablename__ = 'devoluciones'

    id = Column(Integer, primary_key=True, autoincrement=True)
    prestamo_id = Column(Integer, ForeignKey('prestamos.id'), nullable=False)
    fecha_devolucion = Column(DateTime, server_default=func.now())
    estado_libro = Column(String(20), default='bueno')  # bueno, dañado, perdido
    observaciones = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    prestamo = relationship('Prestamo', backref='devoluciones')

    def to_dict(self):
        return {
            'id': self.id,
            'prestamo_id': self.prestamo_id,
            'fecha_devolucion': self.fecha_devolucion.isoformat() if self.fecha_devolucion else None,
            'estado_libro': self.estado_libro,
            'observaciones': self.observaciones,
            'prestamo': self.prestamo.to_dict() if self.prestamo else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
