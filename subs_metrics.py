from datetime import date, datetime, timedelta
from pymongo import MongoClient
import pandas as pd
from config import (
    MONGO_URI, #string de conexión a la Mongo (solo lectura)
    MONGO_DB_USERS, # base de datos Users
    MONGO_COLLECTION_SUBSCRIPTIONS, # colección subscriptions
    MONGO_COLLECTION_STRIPE_UPDATES, # colección stripe-updates
    MONGO_DB_TME_CHARTS, # base de datos TranscribeMe-charts
    MONGO_COLLECTION_TGO_SUBS, # colección de tgo-subscriptions
    MONGO_COLLECTION_MP_PAYMENTS, # colección mp-payments
    MONGO_COLLECTION_STRIPE_PAYMENTS # colección stripe-payments
    )
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
        self.stripe_payments = self.db_tme_charts[MONGO_COLLECTION_STRIPE_PAYMENTS]

    def get_subs_data(self):
        """
        Busca las suscripciones en la Mongo
        Retorna:
        subs: lista de documentos (diccionarios) encontrados
        """
        match_stage = {
            "$match": {
                "status": {"$ne": "cancelled"},
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
    
    def get_active_subs_data(self):
        """
        Busca las suscripciones activas en la Mongo, usando pipeline de agregación de Mongo DB
         
        Parámetros:
        start_date (str): inicio del rango de fechas 
        end_date (str): fin del rango de fechas
    
        Retorna:
        subs: lista de documentos (diccionarios) encontrados
        """
        match_stage = {
            "$match": {
                "status": {
                    "$in": ['active', 'authorized']
                },
            }
        }

        project_stage = {
            "$project": {
                "user_id": 1,
                "provider": 1,
                "status": 1,
                "source": 1,
                "reason": 1,
                # "start_date": { "$substr": ["$start_date", 0, 10] },
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
                    "$gte": start.strftime('%Y-%m-%dT00:00:00.000Z'),
                    "$lt": end.strftime('%Y-%m-%dT00:00:00.000Z')
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

    def get_stripe_subs_per_month(self, start_date, end_date):
        """"
        Obtiene la cantidad de suscripciones de TranscribeMe creadas por mes desde Stripe.
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        valores = ['new_subscription', 'subscription_already_created']
        query = {
            "description": {"$in": valores}, 
            # 'timestamp': {"$gte": "2025-01-01T00:00:00Z"}
            "timestamp": {
                    "$gte": start.strftime('%Y-%m-%dT00:00:00.000Z'),
                    "$lt": end.strftime('%Y-%m-%dT00:00:00.000Z')
            },
        }
        proj = {"_id": 0, "timestamp": 1, "user_id":1, 'source':1, 
                'subscription_id':1, 'plan_id': 1, 'customerId': 1}

        docs = self.stripe_updates.find(query, proj)
        mongo_info = pd.DataFrame(docs)
        mongo_info['timestamp'] = pd.to_datetime(mongo_info['timestamp'], errors='coerce')
        stripe_subs_per_month = (
            mongo_info
            .groupby(mongo_info['timestamp'].dt.to_period('M').dt.to_timestamp())
            .agg(count=('timestamp', 'size'))
        )
        if not stripe_subs_per_month.empty:
            print ("Stripe subs per month found")
        return stripe_subs_per_month
    
    def get_canceladas_stripe_per_month(self, start_date, end_date):
        """
        Obtiene la cantidad de suscripciones de TranscribeMe canceladas por mes desde Stripe.
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        query = {
            "description": "subscription_cancelled", 
            # 'timestamp': {"$gte": "2025-01-01T00:00:00Z"}
            "timestamp": {
                    "$gte": start.strftime('%Y-%m-%dT00:00:00.000Z'),
                    "$lt": end.strftime('%Y-%m-%dT00:00:00.000Z')
            },
        }
        proj = {"_id": 0, "timestamp": 1,}

        docs = self.stripe_updates.find(query, proj)
        canceladas_mongo = pd.DataFrame(docs)

        canceladas_mongo['timestamp'] = pd.to_datetime(canceladas_mongo['timestamp'], errors='coerce')
        canceladas_stripe_per_month = (
            canceladas_mongo
            .groupby(canceladas_mongo['timestamp'].dt.to_period('M').dt.to_timestamp())
            .agg(count=('timestamp', 'size'))
        )
        
        if not canceladas_stripe_per_month.empty:
            print ("Canceladas Stripe per month found")
        return canceladas_stripe_per_month
    
    def get_incomplete_stripe_per_month(self, start_date, end_date):
        """
        Obtiene la cantidad de suscripciones de TranscribeMe incompletas por mes desde Stripe.
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        
        query = {
            "description": "subscription_incomplete_expired", 
            # 'timestamp': {"$gte": "2025-01-01T00:00:00Z"}
            "timestamp": {
                    "$gte": start.strftime('%Y-%m-%dT00:00:00.000Z'),
                    "$lt": end.strftime('%Y-%m-%dT00:00:00.000Z')
            },
        }
        proj = {"_id": 0, "timestamp": 1,}

        docs = self.stripe_updates.find(query, proj)
        incomplete_mongo = pd.DataFrame(docs)

        incomplete_mongo['timestamp'] = pd.to_datetime(incomplete_mongo['timestamp'], errors='coerce')
        incomplete_stripe_per_month = (
            incomplete_mongo
            .groupby(incomplete_mongo['timestamp'].dt.to_period('M').dt.to_timestamp())
            .agg(count=('timestamp', 'size'))
        )

        if not incomplete_stripe_per_month.empty:
            print ("Incomplete Stripe per month found")
        return incomplete_stripe_per_month
    
    def get_tgo_subs(self, selector = 'Total'):
        pipeline = [
            {"$project": {
                         "_id": 0,
                         "status": 1,
                         "created": 1,
                         "ended_at": 1,
                         "plan": "$plan.nickname"}}
        ]
        docs = self.tgo_subs.aggregate(pipeline)
        all_tgo_subs = pd.DataFrame(docs)
        
        if selector == 'Plan Basic':
            all_tgo_subs = all_tgo_subs[all_tgo_subs['plan']=='Basic']
        elif selector == 'Plan Plus':
            all_tgo_subs = all_tgo_subs[all_tgo_subs['plan']=='Plus']
        elif selector == 'Plan Business':
            all_tgo_subs = all_tgo_subs[all_tgo_subs['plan']=='Business']

        canceled = all_tgo_subs[all_tgo_subs['status'] == 'canceled'].copy()
        incomplete = all_tgo_subs[all_tgo_subs['status'] == 'incomplete_expired'].copy()
        
        created_2025 = all_tgo_subs[all_tgo_subs['created'] >= '2025-01-01'].copy()     
        canceled_2025 = canceled[canceled['ended_at'] >= '2025-01-01'].copy()
        incomplete_2025 = incomplete[incomplete['ended_at']>= '2025-01-01'].copy()
        
        created_2025['created'] = pd.to_datetime(created_2025['created'], errors='coerce')
        tgo_2025_subs_per_month = (
            created_2025
            .groupby(created_2025['created'].dt.to_period('M').dt.to_timestamp())
            .agg(count=('created', 'size'))
        )

        canceled_2025['ended_at'] = pd.to_datetime(canceled_2025['ended_at'], errors='coerce')
        tgo_canceled_per_month = (
            canceled_2025
            .groupby(canceled_2025['ended_at'].dt.to_period('M').dt.to_timestamp())
            .agg(count=('ended_at', 'size'))
        )

        incomplete_2025['ended_at'] = pd.to_datetime(incomplete_2025['ended_at'], errors='coerce')
        tgo_incomplete_per_month = (
            incomplete_2025
            .groupby(incomplete_2025['ended_at'].dt.to_period('M').dt.to_timestamp())
            .agg(count=('ended_at', 'size'))
        )
        if not tgo_2025_subs_per_month.empty:
            print ("TGO subs per month found")
        if not tgo_canceled_per_month.empty:
            print ("TGO canceled subs per month found")
        if not tgo_incomplete_per_month.empty:
            print ("TGO incomplete subs per month found")
        return tgo_2025_subs_per_month, tgo_canceled_per_month, tgo_incomplete_per_month

    def get_tme_active_stripe_subs(self):
        query = {'status': "active"}
        total = self.subscriptions.count_documents(query)
        return total
    
    def get_tgo_active_stripe_subs(self):
        query = {'status': "active"}
        total = self.tgo_subs.count_documents(query)
        return total

    def get_total_active_mp_subs(self):
        mp_planes = ['TranscribeMe Plus 10d', 'TranscribeMe Plus discount', 'TranscribeMe Plus 2',
                 'TranscribeMe Plus', 'TranscribeMe Plus - Anual con 3 meses gratis', 
                 'TranscribeMe Plus - mensual 20% off']
        query = {'status': "authorized", "reason":{"$in": mp_planes}}
        total = self.subscriptions.count_documents(query)
        return total
    
    def get_last_month_mp_income(self):
        # Fecha de hoy
        today = date.today()

        # Primer día del mes actual
        first_day_this_month = today.replace(day=1)

        # Primer día del mes pasado
        first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)

        # Primer día de este mes = límite superior
        start_date = first_day_last_month.strftime("%Y-%m-%d")
        end_date = first_day_this_month.strftime("%Y-%m-%d")
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
    
    def get_last_month_stripe_income(self):
        """
        
        """
        # Fecha de hoy
        today = date.today()

        # Primer día del mes actual
        first_day_this_month = today.replace(day=1)

        # Primer día del mes pasado
        first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)

        # Primer día de este mes = límite superior
        start_date = first_day_last_month.strftime("%Y-%m-%d")
        end_date = first_day_this_month.strftime("%Y-%m-%d")
        pipeline = [
            {"$match":{
                "status": 'succeeded',
                # 'currency': 'usd',
                "created":{"$gte": start_date, "$lt": end_date}
                }
            },
            {"$group":{
                # "_id": None,
                '_id': "$currency",
                "total":{"$sum": "$amount"}
                }
            },
            {"$project": {
                'currency': '$_id',
                "total":1
                }
            }
        ]
        cursor = self.stripe_payments.aggregate(pipeline)
        df = pd.DataFrame(list(cursor))

        # Conversión de monedas extranjera a USD
        API_KEY = "7b7af54652e5c42dcaeabdb8"  

        for idx, row in df.iterrows():
            currency = row['currency'].upper()
            amount = row['total']
            if currency != 'USD':
                try:
                    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{currency}/USD/{amount}"
                    response = requests.get(url)
                    data = response.json()
            
                    if data['result'] == 'success':
                        df.at[idx, 'total'] = data['conversion_result']
                        df.at[idx, 'currency'] = 'USD'
                    else:
                        print(f"Error convirtiendo {currency}: {data}")
                
                except Exception as e:
                    print(f"Error con {currency}: {e}")
        total = float(df['total'].sum()) if not df.empty else 0
        return total
    
    def get_monthly_stripe_payments(self):
        """
        """
        docs = self.stripe_payments.find()
        all_payment_intents_created = pd.DataFrame(docs)
        return all_payment_intents_created

    def get_dolar_argentina(self):
        # Api para obtener el precio del dólar oficial
        # "https://dolarapi.com/docs/argentina/operations/get-dolar-oficial.html"
        url = "https://dolarapi.com/v1/dolares/oficial"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()  
        else:
            print("Error:", response.status_code)
            data = {"venta": "No se pudo extraer el valor del dólar, ingrese manualmente"}
        valor_venta_oficial = data['venta']
        return valor_venta_oficial
    
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
        if not df.empty:
            print ("MP planes found")
        return df
    
    def process_mp_subscriptions_data(self, data):
        """
        Process the Mercado Pago subscriptions data to prepare it for visualization.

        Args:
            data (JSON): Mercado Pago subscriptions data stored in JSON format.
        Returns:
            pd.DataFrame: Processed DataFrame with necessary columns.
        """
        if not data:
            print("No MP data provided for processing.")
            return pd.DataFrame(columns=['month', 'creations_count', 'cancelations_count', 'net_subscriptions'])

        df = pd.DataFrame(data)

        # Separo solo las columnas que me interesan
        df = df[['status', 'start_date', 'last_charge_date', 'billing_day']].copy()

        # 1. Convertir start_date a datetime
        df['start_date'] = pd.to_datetime(df['start_date'])
        df['start_month'] = df['start_date'].dt.to_period('M').dt.to_timestamp()

        # 2. Cuento por mes
        creations_df = df['start_month'].value_counts().reset_index()
        creations_df.columns = ['month', 'creations_count']

        # 3. Ordeno cronológicamente
        creations_df = creations_df.sort_values('month')

        # 4. Filtrar cancelados
        cancelados_df = df[df['status'] == 'cancelled'].copy()

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

        # 7. Crear cancelation_month en formato datetime (primer día del mes)
        cancelados_df['cancelation_month'] = cancelados_df['expiration_date'].dt.to_period('M').dt.to_timestamp()

        # 8. Agrupar cancelaciones por mes
        cancelados_df = cancelados_df['cancelation_month'].value_counts().reset_index()
        cancelados_df.columns = ['month', 'cancelations_count']
        cancelados_df = cancelados_df.sort_values('month')

        # 9. Unir creaciones y cancelaciones
        merged_df = pd.merge(
            creations_df,
            cancelados_df,
            on='month',
            how='left'
        ).fillna(0)

        # 10. Calcular suscripciones netas
        merged_df['net_subscriptions'] = merged_df['creations_count'] - merged_df['cancelations_count']

        # 11. Filtrar solo los meses de 2025
        merged_df = merged_df[merged_df['month'].dt.year == 2025]

        return merged_df

    
    def get_mp_payments(self, start, end):
        pipeline = [
            {"$match":{
                "date_created":{"$gte": start, "$lte": end}
                }
            },
            {"$project": {
                "_id":0,
                'date_created':1,
                "date_approved":1,
                "description":1,
                'operation_type':1,
                'status': 1,
                "transaction_amount":1
                }
            }
        ]
        result = list(self.mp_payments.aggregate(pipeline))
        if not result:
            print ("No se encontraron datos entre la fecha ingresada")
        df = pd.DataFrame(result)

        if not df.empty:
            print ("MP payments found")
        return df 

    def get_totales_por_mes(self, mp_df, stripe_creations_df, stripe_cancels_df, stripe_incomplete_df,
                            tgo_subs_per_month, tgo_canceled_per_month, tgo_incomplete_per_month):
        """
        Une MP y Stripe y devuelve un DataFrame con totales de creaciones, cancelaciones e incompletas por mes.

        Args:
            mp_df (pd.DataFrame): salida de process_mp_subscriptions_data()
            stripe_creations_df (pd.DataFrame): salida de get_stripe_subs_per_month()
            stripe_cancels_df (pd.DataFrame): salida de get_canceladas_stripe_per_month()
            stripe_incomplete_df (pd.DataFrame): salida de get_incomplete_stripe_per_month()

        Returns:
            pd.DataFrame con columnas:
                - month
                - total_creations
                - total_cancellations
                - total_incomplete
                - net_total
        """

        # Normalizar formato de Stripe (para tener columna 'month')
        stripe_creations_df = stripe_creations_df.reset_index().rename(columns={'timestamp': 'month', 'count': 'tme_stripe_creations'})
        stripe_cancels_df = stripe_cancels_df.reset_index().rename(columns={'timestamp': 'month', 'count': 'tme_stripe_cancellations'})
        stripe_incomplete_df = stripe_incomplete_df.reset_index().rename(columns={'timestamp': 'month', 'count': 'tme_stripe_incomplete'})
        tgo_subs_per_month = tgo_subs_per_month.reset_index().rename(columns={'created': 'month', 'count': 'tgo_stripe_creations'})
        tgo_canceled_per_month = tgo_canceled_per_month.reset_index().rename(columns={'ended_at': 'month', 'count': 'tgo_stripe_cancellations'})
        tgo_incomplete_per_month = tgo_incomplete_per_month.reset_index().rename(columns={'ended_at': 'month', 'count': 'tgo_stripe_incomplete'})

        # Merge progresivo
        merged = pd.merge(mp_df[['month', 'creations_count', 'cancelations_count']], 
                      stripe_creations_df, on='month', how='outer')
        merged = pd.merge(merged, stripe_cancels_df, on='month', how='outer')
        merged = pd.merge(merged, stripe_incomplete_df, on='month', how='outer')
        merged = pd.merge(merged, tgo_subs_per_month, on='month', how='outer')
        merged = pd.merge(merged, tgo_canceled_per_month, on='month', how='outer')
        merged = pd.merge(merged, tgo_incomplete_per_month, on='month', how='outer')

        # Rellenar NaN con 0
        merged = merged.fillna(0)

        # Calcular totales
        merged['total_creations'] = merged['creations_count'] + merged['tme_stripe_creations'] + merged['tgo_stripe_creations']
        merged['total_cancellations'] = merged['cancelations_count'] + merged['tme_stripe_cancellations'] +  merged ['tgo_stripe_cancellations']
        merged['total_incomplete'] = merged['tme_stripe_incomplete'] + merged['tgo_stripe_incomplete']
        merged['net_total'] = merged['total_creations'] - merged['total_cancellations'] - merged['total_incomplete']

        # Ordenar cronológicamente
        merged = merged.sort_values('month')

        return merged[['month', 'total_creations', 'total_cancellations', 'total_incomplete', 'net_total']]

    def get_stripe_succeeded_subscription_payments (self, start, end):
        pipeline = [
            {"$match":{
                "status": 'succeeded',
                "created":{"$gte": start, "$lt": end},
                'statement_descriptor': {"$ne": None},
                }
            },
            {"$project": {
                "_id":0,
                "created":1,
                "statement_descriptor":1,
                "amount":1,
                'currency':1
                }
            }
        ]
        result = list(self.stripe_payments.aggregate(pipeline))
        if not result:
            print ("No se encontraron datos entre la fecha ingresada")
        df = pd.DataFrame(result)

        descriptions = {
            'Plan Basic': 1.5,
            'Plan Plus': 30,
            'Plan Business': 100,
            'Plus RoW': 3.38,
            'Telegram': 2.42,
            'Plus US / ESP': 5.32,
            'Plus RoW Anual': 27.55,
            'Plus US / ESP Anual': 42.56,
        }

        # Invertir el diccionario: ahora mapea amount -> description
        amount_to_desc = {v: k for k, v in descriptions.items()}

        # Crear la nueva columna en df
        df['description'] = df['amount'].map(amount_to_desc).fillna('Recarga')
        if not df.empty:
            print ("Stripe succeeded subscription payments found")
        return df 
    
    def get_stripe_succeeded_extra_credit_payments (self, start, end):
        pipeline = [
            {"$match":{
                "status": 'succeeded',
                "created":{"$gte": start, "$lt": end},
                "statement_descriptor": {"$eq": None},
                }
            },
            {"$project": {
                "_id":0,
                "created":1,
                "amount":1,
                'currency':1
                }
            }
        ]
        result = list(self.stripe_payments.aggregate(pipeline))
        if not result:
            print ("No se encontraron datos entre la fecha ingresada")
        df = pd.DataFrame(result)

        df['created'] = pd.to_datetime(df['created'])
        df_per_month = (
            df
            .groupby([df['created'].dt.to_period('M').dt.to_timestamp(), 'currency'])
            .agg(income=('amount', 'sum'))
            .reset_index()
        )

        API_KEY = "ea24fd9fe9ec91d1cafdb47b"  

        for idx, row in df_per_month.iterrows():
            currency = row['currency'].upper()
            amount = row['income']
            if currency != 'USD':
                try:
                    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{currency}/USD/{amount}"
                    response = requests.get(url)
                    data = response.json()
            
                    if data['result'] == 'success':
                        df_per_month.at[idx, 'income'] = data['conversion_result']
                        df_per_month.at[idx, 'currency'] = 'USD'
                    else:
                        print(f"Error convirtiendo {currency}: {data}")
                
                except Exception as e:
                    print(f"Error con {currency}: {e}")

        df_per_month['created'] = pd.to_datetime(df_per_month['created'])
        df_per_month = (
            df_per_month
            .groupby(df_per_month['created'].dt.to_period('M').dt.to_timestamp())
            .agg(income=('income', 'sum'))
            .reset_index()
        )
        df_per_month['income'] = round(df_per_month['income'], 2)
        if not df_per_month.empty:
            print ("Stripe succeeded extra credit payments found")
        return df_per_month 
    

    def total_income (self, mp_payments, stripe_subs_payments, extra_credit_income):
        mp_income = mp_payments.copy()
        stripe_subs_income = stripe_subs_payments.copy()
        stripe_extra_income = extra_credit_income.copy()
        dolar = self.get_dolar_argentina()
        mp_income['date_approved'] = pd.to_datetime(mp_income['date_approved'])
        stripe_subs_income['created'] = pd.to_datetime(stripe_subs_income['created'])
        stripe_extra_income['created'] = pd.to_datetime(stripe_extra_income['created'])

        mp_income_per_month = (
            mp_income
            .groupby(mp_income['date_approved'].dt.to_period('M').dt.to_timestamp())
            .agg(mp_income=('transaction_amount', 'sum'))
            .reset_index()
        )
        mp_income_per_month['mp_income'] = round(mp_income_per_month['mp_income'] / dolar, 2)

        stripe_subs_income_per_month = (
            stripe_subs_income
            .groupby(stripe_subs_income['created'].dt.to_period('M').dt.to_timestamp())
            .agg(stripe_subs_income=('amount', 'sum'))
            .reset_index()
        )
        total = pd.merge(mp_income_per_month, stripe_subs_income_per_month, left_on='date_approved', right_on='created', how='outer')
        total = pd.merge(total, stripe_extra_income, left_on='date_approved', right_on='created', how='outer')
        total = total.fillna(0)
        total['stripe_income'] = round(total['stripe_subs_income'] + total['income'], 2)
        total['total_income'] = total['mp_income'] + total['stripe_subs_income'] + total['income']
        total['total_income'] = round(total['total_income'], 2)
        total = total[['date_approved', 'mp_income', 'stripe_subs_income', 'income', 'stripe_income','total_income']]
        total = total.rename(columns={'date_approved': 'month', 'income': 'extra_credit_income'})   
        return total
