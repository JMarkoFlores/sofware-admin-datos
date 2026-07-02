"""
Modelo para almacenar el estado de conversaciones interactivas con usuarios.
Permite mantener contexto de diálogos de reportes por WhatsApp.
"""

from datetime import datetime, timedelta
from models.base import Base
from sqlalchemy import Column, String, DateTime, Integer, Text


class UserConversation(Base):
    """
    Almacena el estado de conversaciones interactivas con usuarios.
    Permite recuperar el contexto cuando un usuario envía un nuevo mensaje.
    """
    __tablename__ = 'user_conversations'

    id = Column(Integer, primary_key=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    state = Column(String(50), default='idle')  # idle, menu, generating_report
    current_report_type = Column(String(50), nullable=True)  # tipo de reporte seleccionado
    last_message_time = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    context_data = Column(Text, nullable=True)  # JSON con datos adicionales
    session_id = Column(String(100), nullable=True)  # ID único de sesión

    def __repr__(self):
        return f"<UserConversation {self.phone_number} - {self.state}>"

    @staticmethod
    def get_or_create(phone_number):
        """Obtiene o crea una conversación para un usuario."""
        from models.base import db
        
        conv = UserConversation.query.filter_by(phone_number=phone_number).first()
        if not conv:
            conv = UserConversation(phone_number=phone_number)
            db.session.add(conv)
            db.session.commit()
        return conv

    @staticmethod
    def is_session_active(phone_number, timeout_minutes=30):
        """Verifica si la sesión de un usuario sigue activa."""
        conv = UserConversation.query.filter_by(phone_number=phone_number).first()
        if not conv:
            return False
        
        time_diff = datetime.utcnow() - conv.last_message_time
        return time_diff < timedelta(minutes=timeout_minutes)

    def update_state(self, state, report_type=None, context_data=None):
        """Actualiza el estado de la conversación."""
        from models.base import db
        
        self.state = state
        self.current_report_type = report_type
        self.last_message_time = datetime.utcnow()
        if context_data:
            self.context_data = context_data
        db.session.commit()

    def reset(self):
        """Reinicia la conversación al estado 'idle'."""
        from models.base import db
        
        self.state = 'idle'
        self.current_report_type = None
        self.last_message_time = datetime.utcnow()
        self.context_data = None
        db.session.commit()
