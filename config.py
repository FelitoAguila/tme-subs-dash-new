import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# Configuración para métricas de suscripciones
MONGO_DB_USERS = 'Users'
MONGO_COLLECTION_SUBSCRIPTIONS = 'subscriptions'     # para ver creación, status, provider, planes de mp, source
MONGO_COLLECTION_STRIPE_UPDATES = "stripe-updates"   # para ver las cancelaciones de suscripciones

MONGO_DB_TME_CHARTS = 'TranscribeMe-charts'
MONGO_COLLECTION_TGO_SUBS = 'tgo-subscriptions'
MONGO_COLLECTION_MP_PAYMENTS = 'mp-payments'
MONGO_COLLECTION_STRIPE_PAYMENTS = 'stripe-payments'

# Configuración para métricas de TGO
MONGO_DB_TGO = 'B2B'
MONGO_COLLECTION_ONBOARDING_TGO = 'onboardings'
MONGO_COLLECTION_TGO_CALLS = 'transcribego-calls'

# API KEY exchange rates
API_KEY = os.getenv("API_KEY_DEV", "")
