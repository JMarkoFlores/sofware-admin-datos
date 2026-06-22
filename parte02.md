# ============================================================

# Archivo de configuración de entorno

# Copiar este archivo como .env y completar los valores reales

# ============================================================

# --------------------------------------------------

# Configuración de SQL Server

# --------------------------------------------------

DB_USER=
DB_PASSWORD=
DB_SERVER=Jeanmarko
DB_NAME=TenebrosaOLTP
DB_TRUSTED_CONNECTION=yes
DB_DRIVER=ODBC Driver 17 for SQL Server

# --------------------------------------------------

# Configuración de WhatsApp (WhatsApp Business Cloud API)

# --------------------------------------------------

# Obtener de: https://developers.facebook.com/apps

WHATSAPP_PROVIDER=whatsapp_business_api
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WHATSAPP_DESTINATION_PHONE=5215512345678

# --------------------------------------------------

# Configuración alternativa: Twilio

# Descomentar y usar si se prefiere Twilio

# --------------------------------------------------

# WHATSAPP_PROVIDER=twilio

# TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# TWILIO_FROM_NUMBER=whatsapp:+14155238886

# TWILIO_TO_NUMBER=whatsapp:+5215512345678

# --------------------------------------------------

# Configuración alternativa: UZAPI

# UZAPI conecta tu WhatsApp personal via QR

# Documentación: https://documenter.getpostman.com/view/131526/U16hsmcg

# --------------------------------------------------

WHATSAPP_PROVIDER=uzapi
UZAPI_ENDPOINT=https://teste.uzapi.com.br:3333
UZAPI_TOKEN=
UZAPI_SESSION=1
UZAPI_SESSION_KEY=1
UZAPI_DESTINATION_PHONE=51954502496
UZAPI_SEND_PATH=/sendText
UZAPI_PHONE_FIELD=number
UZAPI_MESSAGE_FIELD=text
UZAPI_AUTH_HEADER=

# --------------------------------------------------

# Configuración de la aplicación

# --------------------------------------------------

APP_LOG_LEVEL=INFO
APP_LOG_FILE=logs/monitoreo.log
APP_INTERVAL_MINUTES=30
APP_TIMEZONE=America/Mexico_City

# --------------------------------------------------

# Configuración de monitoreo

# --------------------------------------------------

# Tabla de auditoría en SQL Server

AUDIT_TABLE=dbo.MonitoreoAuditoria
