import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_ANALYTICS = 'Analytics'
MONGO_COLLECTION_DAU = 'dau'

# Configuración para métricas de suscripciones
MONGO_DB_USERS = 'Users'
MONGO_COLLECTION_SUBSCRIPTIONS = 'subscriptions'