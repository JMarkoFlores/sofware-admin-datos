from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base


class Multa(Base):
    __tablename__ = 'multas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    lector_id = Column(Integer, ForeignKey('lectores.id'), nullable=False)
    prestamo_id = Column(Integer, ForeignKey('prestamos.id'))
    monto = Column(Numeric(10, 2), nullable=False)
    motivo = Column(String(200))
    pagada = Column(Boolean, default=False)
    fecha_pago = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    lector = relationship('Lector', backref='multas')
    prestamo = relationship('Prestamo', backref='multas')

    def to_dict(self):
        return {
            'id': self.id,
            'lector_id': self.lector_id,
            'prestamo_id': self.prestamo_id,
            'monto': float(self.monto) if self.monto else None,
            'motivo': self.motivo,
            'pagada': self.pagada,
            'fecha_pago': self.fecha_pago.isoformat() if self.fecha_pago else None,
            'lector': self.lector.to_dict() if self.lector else None,
            'prestamo': self.prestamo.to_dict() if self.prestamo else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
