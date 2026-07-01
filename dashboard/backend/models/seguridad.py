
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from models.base import Base


class IntentoLogin(Base):
    __tablename__ = 'intentos_login'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False)
    ip_address = Column(String(50))
    exitoso = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class UsuarioBloqueado(Base):
    __tablename__ = 'usuarios_bloqueados'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    motivo = Column(String(255), default='Intentos fallidos de login')
    bloqueado_hasta = Column(DateTime)
    bloqueado_por = Column(String(50), default='Sistema')
    desbloqueado = Column(Boolean, default=False)
    desbloqueado_por = Column(String(50))
    desbloqueado_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'motivo': self.motivo,
            'bloqueado_hasta': self.bloqueado_hasta.isoformat() if self.bloqueado_hasta else None,
            'bloqueado_por': self.bloqueado_por,
            'desbloqueado': self.desbloqueado,
            'desbloqueado_por': self.desbloqueado_por,
            'desbloqueado_at': self.desbloqueado_at.isoformat() if self.desbloqueado_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

