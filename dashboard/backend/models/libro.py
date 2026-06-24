from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base


class Libro(Base):
    __tablename__ = 'libros'

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(200), nullable=False)
    isbn = Column(String(20), unique=True)
    anio_publicacion = Column(Integer)
    editorial = Column(String(100))
    ejemplares_total = Column(Integer, default=1)
    ejemplares_disponibles = Column(Integer, default=1)
    autor_id = Column(Integer, ForeignKey('autores.id'))
    categoria_id = Column(Integer, ForeignKey('categorias.id'))
    created_at = Column(DateTime, server_default=func.now())

    autor = relationship('Autor', backref='libros')
    categoria = relationship('Categoria', backref='libros')

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'isbn': self.isbn,
            'anio_publicacion': self.anio_publicacion,
            'editorial': self.editorial,
            'ejemplares_total': self.ejemplares_total,
            'ejemplares_disponibles': self.ejemplares_disponibles,
            'autor_id': self.autor_id,
            'categoria_id': self.categoria_id,
            'autor': self.autor.to_dict() if self.autor else None,
            'categoria': self.categoria.to_dict() if self.categoria else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
