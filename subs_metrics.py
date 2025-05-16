from datetime import datetime, timedelta
from pymongo import MongoClient
import pandas as pd
from config import MONGO_URI, MONGO_DB_USERS, MONGO_COLLECTION_SUBSCRIPTIONS
from get_country import getCountry


class SubscriptionMetrics:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB_USERS]
        self.collection = self.db[MONGO_COLLECTION_SUBSCRIPTIONS]

    def get_subs_data(self, start_date, end_date):
        """
        Busca las suscripciones en la Mongo, creadas en un rango de fechas
        usando pipeline de agregación de Mongo DB
         
        Parámetros:
        start_date (str): inicio del rango de fechas 
        end_date (str): fin del rango de fechas
    
        Retorna:
        subs: lista de documentos (diccionarios) encontrados
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        match_stage = {
            "$match": {
                "start_date": {
                    "$gte": start.strftime('%Y-%m-%dT00:00:00.000-04:00'),
                    "$lt": end.strftime('%Y-%m-%dT00:00:00.000-04:00')
                }
            }
        }

        project_stage = {
            "$project": {
                "user_id": 1,
                "provider": 1,
                "status": 1,
                "source": 1,
                "reason": 1,
                "start_date": { "$substr": ["$start_date", 0, 10] },
                "_id": 0
            }
        }

        pipeline = [match_stage, project_stage]
        subs = list(self.collection.aggregate(pipeline))
        return subs
    
    def asign_countries (self, doc_list):
        """
        Asigna el país a cada documento de la lista y devuelve un dataframe con el resultado
         
        Parámetros:
        doc_list (list_dic): lista de documentos (diccionarios)
    
        Retorna:
        pd.DataFrame: dataframe con los resultados
        """
        for doc in doc_list:
            if doc['source'] == "t":
                country = "Telegram"
            else:
                user_id = doc['user_id']
                user_phone = '+' + str(user_id)
                country = getCountry(user_phone)
            doc['country'] = country
        return pd.DataFrame(doc_list)
    
    def assign_provider_default(self, df):
        """
        Asigna el valor 'mp' a los valores faltantes en la columna 'provider' de un DataFrame.
    
        Parámetros:
        df (pandas.DataFrame): DataFrame que contiene la columna 'provider'.
    
        Retorna:
        pandas.DataFrame: DataFrame con los valores faltantes en 'provider' reemplazados por 'mp'.
    
        Raises:
        KeyError: Si la columna 'provider' no existe en el DataFrame.
        """
        try:
            # Verificar si la columna 'provider' existe
            if 'provider' not in df.columns:
                raise KeyError("La columna 'provider' no existe en el DataFrame")
        
            # Reemplazar valores faltantes (NaN, None) en la columna 'provider' con 'mp'
            df['provider'] = df['provider'].fillna('mp')
        
            return df
    
        except Exception as e:
            print(f"Error: {e}")
            return df  # Retorna el DataFrame sin cambios en caso de error
        
    def subs_all(self, df, group_by='day', status=None, reason=None, source=None, country=None, provider=None):
        """
        Analiza suscripciones, agrupando por día o mes, con filtros opcionales.
    
        Args:
            df (pandas.DataFrame): DataFrame con las columnas ['status', 'reason', 'user_id', 'source', 
                                   'start_date', 'country', 'provider']
            group_by (str): 'day' o 'month' para agrupar los resultados
            status (str or list): Valor(es) para filtrar por status, 'all' para considerar todos
            reason (str or list): Valor(es) para filtrar por reason, 'all' para considerar todos
            source (str or list): Valor(es) para filtrar por source, 'all' para considerar todos
            country (str or list): Valor(es) para filtrar por country, 'all' para considerar todos
            provider (str or list): Valor(es) para filtrar por provider, 'all' para considerar todos
    
        Returns:
            pandas.DataFrame: DataFrame con la cantidad de suscripciones agrupadas por día o mes y 
                         las columnas de filtro especificadas
        """
        # Crear una copia del DataFrame para no modificar el original
        df_copy = df.copy()
    
        # Convertir start_date a datetime si es string
        if df_copy['start_date'].dtype == 'object':
            df_copy['start_date'] = pd.to_datetime(df_copy['start_date'])

        # Aplicar filtros adicionales si se especifican
        if status is not None and status != 'all':
            if isinstance(status, list):
                df_copy = df_copy[df_copy['status'].isin(status)]
            else:
                df_copy = df_copy[df_copy['status'] == status]
    
        if reason is not None and reason != 'all':
            if isinstance(reason, list):
                df_copy = df_copy[df_copy['reason'].isin(reason)]
            else:
                df_copy = df_copy[df_copy['reason'] == reason]
    
        if source is not None and source != 'all':
            if isinstance(source, list):
                df_copy = df_copy[df_copy['source'].isin(source)]
            else:
                df_copy = df_copy[df_copy['source'] == source]
    
        if country is not None and country != 'all':
            if isinstance(country, list):
                df_copy = df_copy[df_copy['country'].isin(country)]
            else:
                df_copy = df_copy[df_copy['country'] == country]
    
        if provider is not None and provider != 'all':
            if isinstance(provider, list):
                df_copy = df_copy[df_copy['provider'].isin(provider)]
            else:
                df_copy = df_copy[df_copy['provider'] == provider]
    
        # Crear la columna de agrupación según el parámetro group_by
        if group_by.lower() == 'day':
            df_copy['date'] = df_copy['start_date'].dt.date
        elif group_by.lower() == 'month':
            df_copy['date'] = df_copy['start_date'].dt.to_period('M').dt.to_timestamp()
        else:
            raise ValueError("El parámetro group_by debe ser 'day' o 'month'")
    
        # Determinar columnas de agrupación adicionales
        group_columns = ['date']
        if status is not None:
            group_columns.append('status')
        if reason is not None:
            group_columns.append('reason')
        if source is not None:
            group_columns.append('source')
        if country is not None:
            group_columns.append('country')
        if provider is not None:
            group_columns.append('provider')
    
        # Agrupar y contar
        result = df_copy.groupby(group_columns).size().reset_index(name='count')
    
        # Formatear el resultado según el tipo de agrupación
        if group_by.lower() == 'day':
            result['date'] = result['date'].astype(str)
        elif group_by.lower() == 'month':
            if isinstance(result['date'].iloc[0], pd.Period):
                result['date'] = result['date'].dt.strftime('%Y-%m')
            else:
                result['date'] = result['date'].dt.strftime('%Y-%m')
        
        return result