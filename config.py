import os
from pymongo import MongoClient

# Usar variable de entorno o valor por defecto para desarrollo
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")

# Otras configuraciones
MONGO_DB_ANALYTICS = 'Analytics'
MONGO_COLLECTION_DAU = 'dau'
MONGO_DB_USERS = 'Users'
MONGO_COLLECTION_SUBSCRIPTIONS = 'subscriptions'