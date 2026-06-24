from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base


class Prestamo(Base):
    __tablename__ = 'prestamos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    lector_id = Column(Integer, ForeignKey('lectores.id'), nullable=False)
    libro_id = Column(Integer, ForeignKey('libros.id'), nullable=False)
    fecha_prestamo = Column(DateTime, server_default=func.now())
    fecha_devolucion_esperada = Column(DateTime, nullable=False)
    fecha_devolucion_real = Column(DateTime)
    estado = Column(String(20), default='activo')  # activo, devuelto, vencido
    observaciones = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    lector = relationship('Lector', backref='prestamos')
    libro = relationship('Libro', backref='prestamos')

    def to_dict(self):
        return {
            'id': self.id,
            'lector_id': self.lector_id,
            'libro_id': self.libro_id,
            'fecha_prestamo': self.fecha_prestamo.isoformat() if self.fecha_prestamo else None,
            'fecha_devolucion_esperada': self.fecha_devolucion_esperada.isoformat() if self.fecha_devolucion_esperada else None,
            'fecha_devolucion_real': self.fecha_devolucion_real.isoformat() if self.fecha_devolucion_real else None,
            'estado': self.estado,
            'observaciones': self.observaciones,
            'lector': self.lector.to_dict() if self.lector else None,
            'libro': self.libro.to_dict() if self.libro else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
