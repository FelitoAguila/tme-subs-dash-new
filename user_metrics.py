from datetime import datetime, timedelta
import pandas as pd
from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB_ANALYTICS, MONGO_COLLECTION_DAU

class UserMetrics:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB_ANALYTICS]
        self.collection = self.db[MONGO_COLLECTION_DAU]
    
    def _parse_date(self, date_str):
        """Convierte una cadena de fecha en formato YYYY-MM-DD a objeto datetime."""
        return datetime.strptime(date_str, '%Y-%m-%d')
    
    def get_daily_active_users(self, start_date, end_date):
        """Calcula el número de usuarios activos por día usando agregaciones de MongoDB."""
        pipeline = [
            {
                '$match': {
                    'dt': {
                        '$gte': start_date,
                        '$lte': end_date
                    }
                }
            },
            {
                '$group': {
                    '_id': '$dt',
                    'active_users': {'$addToSet': '$user_id'}
                }
            },
            {
                '$project': {
                    'date': '$_id',
                    'active_users': {'$size': '$active_users'},
                    '_id': 0
                }
            },
            {
                '$sort': {'date': 1}
            }
        ]
        
        result = list(self.collection.aggregate(pipeline))
        return result
    
    def get_monthly_active_users(self, start_date, end_date):
        """Calcula el número de usuarios activos por mes usando agregaciones de MongoDB."""
        pipeline = [
            {
                '$match': {
                    'dt': {
                        '$gte': start_date,
                        '$lte': end_date
                    }
                }
            },
            {
                '$project': {
                    'user_id': 1,
                    'month': {'$substr': ['$dt', 0, 7]}  # Extraer YYYY-MM
                }
            },
            {
                '$group': {
                    '_id': '$month',
                    'active_users': {'$addToSet': '$user_id'}
                }
            },
            {
                '$project': {
                    'month': '$_id',
                    'active_users': {'$size': '$active_users'},
                    '_id': 0
                }
            },
            {
                '$sort': {'month': 1}
            }
        ]
        
        result = list(self.collection.aggregate(pipeline))
        return result
    
    def get_total_users(self, end_date):
        """Obtiene el número total de usuarios hasta una fecha determinada."""
        pipeline = [
            {
                '$match': {
                    'dt': {'$lte': end_date}
                }
            },
            {
                '$group': {
                    '_id': None,
                    'unique_users': {'$addToSet': '$user_id'}
                }
            },
            {
                '$project': {
                    'count': {'$size': '$unique_users'},
                    '_id': 0
                }
            }
        ]
        
        result = list(self.collection.aggregate(pipeline))
        return result[0]['count'] if result else 0
    
    def get_new_users_by_day(self, start_date, end_date):
        """Calcula nuevos usuarios por día utilizando una estrategia optimizada de agregación."""
        # Obtener la primera aparición de cada usuario
        pipeline = [
            {
                '$sort': {'dt': 1, 'user_id': 1}
            },
            {
                '$group': {
                    '_id': '$user_id',
                    'first_seen': {'$first': '$dt'}
                }
            },
            {
                '$match': {
                    'first_seen': {
                        '$gte': start_date,
                        '$lte': end_date
                    }
                }
            },
            {
                '$group': {
                    '_id': '$first_seen',
                    'new_users': {'$sum': 1}
                }
            },
            {
                '$project': {
                    'date': '$_id',
                    'new_users': 1,
                    '_id': 0
                }
            },
            {
                '$sort': {'date': 1}
            }
        ]
        
        result = list(self.collection.aggregate(pipeline))
        return result
    
    def get_new_users_by_month(self, start_date, end_date):
        """Calcula nuevos usuarios por mes utilizando agregaciones de MongoDB."""
        pipeline = [
            {
                '$sort': {'dt': 1, 'user_id': 1}
            },
            {
                '$group': {
                    '_id': '$user_id',
                    'first_seen': {'$first': '$dt'}
                }
            },
            {
                '$match': {
                    'first_seen': {
                        '$gte': start_date,
                        '$lte': end_date
                    }
                }
            },
            {
                '$project': {
                    'user_id': '$_id',
                    'first_seen': 1,
                    'month': {'$substr': ['$first_seen', 0, 7]}  # Extraer YYYY-MM
                }
            },
            {
                '$group': {
                    '_id': '$month',
                    'new_users': {'$sum': 1}
                }
            },
            {
                '$project': {
                    'month': '$_id',
                    'new_users': 1,
                    '_id': 0
                }
            },
            {
                '$sort': {'month': 1}
            }
        ]
        
        result = list(self.collection.aggregate(pipeline))
        return result
    
    def close_connection(self):
        """Cierra la conexión con MongoDB."""
        self.client.close()