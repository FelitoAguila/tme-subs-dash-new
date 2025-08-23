from datetime import datetime, timedelta
from pymongo import MongoClient
import pandas as pd
from config import (MONGO_URI, MONGO_DB_USERS, MONGO_COLLECTION_SUBSCRIPTIONS, 
                    MONGO_COLLECTION_STRIPE_UPDATES, MONGO_DB_TME_CHARTS, MONGO_COLLECTION_TGO_SUBS,
                    MONGO_COLLECTION_MP_PAYMENTS)
from get_country import getCountry
import requests

class SubscriptionMetrics:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db_users = self.client[MONGO_DB_USERS]
        self.subscriptions = self.db_users[MONGO_COLLECTION_SUBSCRIPTIONS]
        self.stripe_updates = self.db_users[MONGO_COLLECTION_STRIPE_UPDATES]
        self.db_tme_charts = self.client[MONGO_DB_TME_CHARTS]
        self.tgo_subs = self.db_tme_charts[MONGO_COLLECTION_TGO_SUBS]
        self.mp_payments = self.db_tme_charts[MONGO_COLLECTION_MP_PAYMENTS]

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
                },
                "is_experiment_gift":{"$exists": False},
                "is_free_balance_error":{"$exists": False}
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
        subs = list(self.subscriptions.aggregate(pipeline))
        return subs
    
    def get_stripe_cancelation_data (self, start_date, end_date):
        """
        Busca las stripe-updates de cancelaciones de suscripciones en la Mongo, creadas en un rango de fechas
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
                "timestamp": {
                    "$gte": start.strftime('%Y-%m-%dT00:00:00.000-04:00'),
                    "$lt": end.strftime('%Y-%m-%dT00:00:00.000-04:00')
                },
                "description": "subscription_cancelled"
            }
        }

        project_stage = {
            "$project": {
                "user_id": 1,
                "source": 1,
                "timestamp": { "$substr": ["$timestamp", 0, 10] },
                "_id": 0
            }
        }

        pipeline = [match_stage, project_stage]
        stripe_cancelation_data = list(self.stripe_updates.aggregate(pipeline))
        return stripe_cancelation_data

    def get_stripe_creation_data (self, start_date, end_date):
        """
        Busca las stripe-updates de creaciones de suscripciones en la Mongo, creadas en un rango de fechas
        usando pipeline de agregación de Mongo DB
         
        Parámetros:
        start_date (str): inicio del rango de fechas 
        end_date (str): fin del rango de fechas
    
        Retorna:
        subs: lista de documentos (diccionarios) encontrados
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        valores = ['new_subscription', 'subscription_already_created']
        match_stage = {
            "$match": {
                "timestamp": {
                    "$gte": start.strftime('%Y-%m-%dT00:00:00.000-04:00'),
                    "$lt": end.strftime('%Y-%m-%dT00:00:00.000-04:00')
                },
                "description": {"$in": valores}
            }
        }

        project_stage = {
            "$project": {
                "user_id": 1,
                "source": 1,
                "timestamp": { "$substr": ["$timestamp", 0, 10] },
                "_id": 0
            }
        }

        pipeline = [match_stage, project_stage]
        stripe_creation_data = list(self.stripe_updates.aggregate(pipeline))
        return stripe_creation_data
    
    def get_stripe_incomplete_data (self, start_date, end_date):
        """
        Busca las stripe-updates de suscripciones incompletas en la Mongo, creadas en un rango de fechas
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
                "timestamp": {
                    "$gte": start.strftime('%Y-%m-%dT00:00:00.000-04:00'),
                    "$lt": end.strftime('%Y-%m-%dT00:00:00.000-04:00')
                },
                "description": "subscription_incomplete_expired"
            }
        }

        project_stage = {
            "$project": {
                "user_id": 1,
                "source": 1,
                "timestamp": { "$substr": ["$timestamp", 0, 10] },
                "_id": 0
            }
        }

        pipeline = [match_stage, project_stage]
        stripe_incomplete_data = list(self.stripe_updates.aggregate(pipeline))
        return stripe_incomplete_data
    
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
    
    def subscription_balance_df(self, df_subs_created, df_subs_cancelled):
        df_subs_created = df_subs_created.rename(columns={'count': 'creadas'})
        df_subs_cancelled = df_subs_cancelled.rename(columns={'count': 'canceladas'})
        df_balance = pd.merge(df_subs_created, df_subs_cancelled, on=['date', 'country', 'provider'], how='outer').fillna(0)
        df_balance['balance'] = df_balance['creadas'] - df_balance['canceladas']
        return df_balance[["date", "country", "balance"]]

    def get_stripe_subs_per_month(self):
        valores = ['new_subscription', 'subscription_already_created']
        query = {"description": {"$in": valores}, 'timestamp': {"$gte": "2025-01-01T00:00:00Z"}}
        proj = {"_id": 0, "timestamp": 1, "user_id":1, 'source':1, 'subscription_id':1, 'plan_id': 1, 'customerId': 1}

        docs = self.stripe_updates.find(query, proj)
        mongo_info = pd.DataFrame(docs)
        mongo_info['timestamp'] = pd.to_datetime(mongo_info['timestamp'], errors='coerce')
        stripe_subs_per_month = (
            mongo_info
            .groupby(mongo_info['timestamp'].dt.to_period('M').dt.to_timestamp())
            .agg(count=('timestamp', 'size'))
        )
        return stripe_subs_per_month
    
    def get_canceladas_stripe_per_month(self):
        query = {"description": "subscription_cancelled", 'timestamp': {"$gte": "2025-01-01T00:00:00Z"}}
        proj = {"_id": 0, "timestamp": 1,}

        docs = self.stripe_updates.find(query, proj)
        canceladas_mongo = pd.DataFrame(docs)

        canceladas_mongo['timestamp'] = pd.to_datetime(canceladas_mongo['timestamp'], errors='coerce')
        canceladas_stripe_per_month = (
            canceladas_mongo
            .groupby(canceladas_mongo['timestamp'].dt.to_period('M').dt.to_timestamp())
            .agg(count=('timestamp', 'size'))
        )
        return canceladas_stripe_per_month
    
    def get_incomplete_stripe_per_month(self):
        query = {"description": "subscription_incomplete_expired", 'timestamp': {"$gte": "2025-01-01T00:00:00Z"}}
        proj = {"_id": 0, "timestamp": 1,}

        docs = self.stripe_updates.find(query, proj)
        incomplete_mongo = pd.DataFrame(docs)

        incomplete_mongo['timestamp'] = pd.to_datetime(incomplete_mongo['timestamp'], errors='coerce')
        incomplete_stripe_per_month = (
            incomplete_mongo
            .groupby(incomplete_mongo['timestamp'].dt.to_period('M').dt.to_timestamp())
            .agg(count=('timestamp', 'size'))
        )
        return incomplete_stripe_per_month
    
    def get_tgo_subs(self):
        query = {"created": {"$gte": '2025-01-01'}}
        proj = {"_id": 0, "status":1, "created":1, "ended_at":1}

        docs = self.tgo_subs.find(query, proj)
        all_tgo_subs = pd.DataFrame(docs)

        tgo_incomplete_docs = self.tgo_subs.find({"status": 'incomplete_expired',
                                                                "ended_at": {"$gte": '2025-01-01'}}, 
                                                                proj)
        tgo_canceled_docs = self.tgo_subs.find({"status": 'canceled',
                                                                "ended_at": {"$gte": '2025-01-01'}}, 
                                                                proj)
        
        tgo_incomplete = pd.DataFrame(tgo_incomplete_docs)
        tgo_canceled = pd.DataFrame(tgo_canceled_docs)

        all_tgo_subs['created'] = pd.to_datetime(all_tgo_subs['created'], errors='coerce')
        tgo_2025_subs_per_month = (
            all_tgo_subs
            .groupby(all_tgo_subs['created'].dt.to_period('M').dt.to_timestamp())
            .agg(count=('created', 'size'))
        )

        tgo_canceled['ended_at'] = pd.to_datetime(tgo_canceled['ended_at'], errors='coerce')
        tgo_canceled_per_month = (
            tgo_canceled
            .groupby(tgo_canceled['ended_at'].dt.to_period('M').dt.to_timestamp())
            .agg(count=('ended_at', 'size'))
        )

        tgo_incomplete['ended_at'] = pd.to_datetime(tgo_incomplete['ended_at'], errors='coerce')
        tgo_incomplete_per_month = (
            tgo_incomplete
            .groupby(tgo_incomplete['ended_at'].dt.to_period('M').dt.to_timestamp())
            .agg(count=('ended_at', 'size'))
        )
        return tgo_2025_subs_per_month, tgo_canceled_per_month, tgo_incomplete_per_month

    def get_total_active_stripe_subs(self):
        query = {'status': "active"}
        total = self.subscriptions.count_documents(query)
        return total
    
    def get_total_active_mp_subs(self):
        mp_planes = ['TranscribeMe Plus 10d', 'TranscribeMe Plus discount', 'TranscribeMe Plus 2',
                 'TranscribeMe Plus', 'TranscribeMe Plus - Anual con 3 meses gratis', 
                 'TranscribeMe Plus - mensual 20% off']
        query = {'status': "authorized", "reason":{"$in": mp_planes}}
        total = self.subscriptions.count_documents(query)
        return total
    
    def get_mp_income(self):
        start_date = "2025-07-01"
        end_date = "2025-08-01"
        pipeline = [
            {"$match":{
                "status": 'approved',
                "date_approved":{"$gte": start_date, "$lt": end_date}
                }
            },
            {"$group":{
                "_id": None,
                "total":{"$sum": "$transaction_amount"}
                }
            },
            {"$project": {
                "total":1
                }
            }
        ]
        result = list(self.mp_payments.aggregate(pipeline))
        return result[0]["total"] if result else 0
    
    def get_stripe_income(self):
        """
        COMPLETAR
        """
        return 15000
    
    def get_dolar_argentina(self):
        # Api para obtener el precio del dólar oficial
        # "https://dolarapi.com/docs/argentina/operations/get-dolar-oficial.html"
        url = "https://dolarapi.com/v1/dolares/oficial"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()  # o .text según el caso
        else:
            print("Error:", response.status_code)
            data = {"compra": "No se pudo extraer el valor del dólar, ingrese manualmente"}
        valor_compra_oficial = data['compra']
        return valor_compra_oficial
    
    def get_mp_planes(self):
        mp_planes = ['TranscribeMe Plus 10d', 'TranscribeMe Plus discount', 'TranscribeMe Plus 2',
                 'TranscribeMe Plus', 'TranscribeMe Plus - Anual con 3 meses gratis', 
                 'TranscribeMe Plus - mensual 20% off']
        pipeline = [
            {"$match": {
                "status": 'authorized',
                "reason": {"$in": mp_planes}
                }
            },
            {"$group":{
                "_id": "$reason",
                "count": {"$sum":1}
                }
            },
            {"$project": { 
                "_id": 0,
                "reason": "$_id",
                "count": 1
                }
            }
        ]

        docs = list(self.subscriptions.aggregate(pipeline))
        df = pd.DataFrame(docs)
        return df
    
    def process_mp_subscriptions_data(self, data):
        """
        Process the Mercado Pago subscriptions data to prepare it for visualization.
    
        Args:
            data (JSON): Mercado Pago subscriptions data stored in JSON format.
            This should include fields like 'status', 'start_date', 'last_charge_date', and 'billing_day'.
        Returns:
            pd.DataFrame: Processed DataFrame with necessary columns.
        """
        if not data:
            print ("No MP data provided for processing.")
            return pd.DataFrame(columns=['month', 'creations_count', 'cancelations_count', 'net_subscriptions'])
        df = pd.DataFrame(data)
    
        # Separo solo las columnas que me interesan
        df = df[['status', 'start_date', 'last_charge_date', 'billing_day']].copy()
    
        # 1. Obtengo la fecha de inicio de todas las suscripciones
        df['start_date'] = pd.to_datetime(df['start_date'])
        df['start_month'] = df['start_date'].dt.strftime('%b-%Y')

        # 2. Cuento por mes
        creations_df = df['start_month'].value_counts().reset_index()
        creations_df.columns = ['start_month', 'count']

        # 3. Ordeno y formateo
        creations_df['month_for_sorting'] = pd.to_datetime(creations_df['start_month'], format='%b-%Y')
        creations_df = creations_df.sort_values('month_for_sorting').drop(columns='month_for_sorting')

        # 4. Busco solo los cancelados
        cancelados_df = df[df['status']=='cancelled'].copy()

        # 5. Convertir last_charge_date a datetime
        cancelados_df['last_charge_date'] = pd.to_datetime(cancelados_df['last_charge_date'])

        # 6. Crear expiration_date: próximo día 26
        cancelados_df['expiration_date'] = cancelados_df['last_charge_date'].apply(
            lambda x: pd.Timestamp(
                year=x.year + (x.month // 12) if x.day >= 26 else x.year,
                month=(x.month % 12) + 1 if x.day >= 26 else x.month,
                day=26
            )
        )

        # 7. Crear cancelation_month con formato "Mes-Año"
        cancelados_df['cancelation_month'] = cancelados_df['expiration_date'].dt.strftime('%b-%Y')

        # 8. Agrupar la cantidad de cancelaciones por mes
        cancelados_df = cancelados_df['cancelation_month'].value_counts().reset_index()
        cancelados_df.columns = ['cancelation_month', 'cancelations_count']

        # 9. Convertir cancelation_month a datetime para ordenar cronológicamente
        cancelados_df['month_for_sorting'] = pd.to_datetime(cancelados_df['cancelation_month'], format='%b-%Y')
        cancelados_df = cancelados_df.sort_values('month_for_sorting').drop(columns='month_for_sorting')
    
        # 10. Unir los DataFrames de creaciones y cancelaciones
        merged_df = pd.merge(
            creations_df.rename(columns={'start_month': 'month', 'count': 'creations_count'}),
            cancelados_df.rename(columns={'cancelation_month': 'month', 'cancelations_count': 'cancelations_count'}),
            on='month',
            how='left'
        ).fillna(0)  # Rellenar con 0 si no hay datos para un mes en alguna de las series

        # 11. Calcular suscripciones netas
        merged_df['net_subscriptions'] = merged_df['creations_count'] - merged_df['cancelations_count']

        # 12. Ordeno y formateo
        merged_df['month_for_sorting'] = pd.to_datetime(merged_df['month'], format='%b-%Y')
        merged_df = merged_df.sort_values('month_for_sorting').drop(columns='month_for_sorting')

        # Convertir month a datetime
        merged_df['month_dt'] = pd.to_datetime(merged_df['month'], format='%b-%Y')

        # Filtrar solo los meses del 2025
        merged_df = merged_df[merged_df['month_dt'].dt.year == 2025]

        # Opcional: quitar la columna auxiliar
        merged_df = merged_df.drop(columns='month_dt')
        return merged_df
