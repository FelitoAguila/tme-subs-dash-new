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
    
    def daily_subs_by_country(self, start_date, end_date):
        """
        Cuenta la cantidad de usuarios que se registraron por día y por país en un rango de fechas.
    
        Args:
            start_date: Fecha de inicio en formato 'YYYY-MM-DD'
            end_date: Fecha final en formato 'YYYY-MM-DD'
        
        Returns:
            Un DataFrame con fechas en filas, países en columnas y la cantidad de usuarios como valores
        """
    
        # Convertir fechas de string a datetime para filtrar
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        end = end + timedelta(days=1)  # Incluir el último día completo
    
        # Consultar los documentos dentro del rango de fechas
        query = {
            "start_date": {
                "$gte": start.strftime('%Y-%m-%dT00:00:00.000-04:00'),
                "$lt": end.strftime('%Y-%m-%dT00:00:00.000-04:00')
            }
        }
        
        # Obtener solo los campos necesarios
        projection = {
            "start_date": 1,
            "user_id": 1,
            "_id": 0
        }
        
        # Ejecutar la consulta
        documents = list(self.collection.find(query, projection))
        
        # Procesar los resultados para obtener fecha y país
        result_data = []
        
        for doc in documents:
            # Extraer solo la parte de la fecha (YYYY-MM-DD)
            date_str = doc["start_date"][:10]
            
            # Obtener el país a partir del número de teléfono
            user_phone = '+' + str(doc["user_id"] )
            country = getCountry(user_phone)
            
            result_data.append({
                "date": date_str,
                "country": country
            })
        
        # Convertir a DataFrame
        df = pd.DataFrame(result_data)
        
        # Si no hay datos, devolver un DataFrame vacío
        if df.empty:
            return pd.DataFrame()
        
        # Contar por fecha y país
        pivot_df = df.pivot_table(
            index="date", 
            columns="country", 
            aggfunc="size", 
            fill_value=0
        )
        
        # Asegurar que todas las fechas en el rango tengan un valor
        date_range = pd.date_range(start=start_date, end=end_date)
        date_range_str = [date.strftime('%Y-%m-%d') for date in date_range]
        
        # Crear un DataFrame con todas las fechas
        complete_df = pd.DataFrame(index=date_range_str)
        
        # Unir con el pivot_df
        merged_df = complete_df.join(pivot_df, how='left').fillna(0).astype(int)
        
        return merged_df
    
    
    def monthly_subs_by_country(self, start_date, end_date):
        """
        Cuenta la cantidad de usuarios que se registraron por mes y por país en un rango de fechas.

        Args:
            start_date: Fecha de inicio en formato 'YYYY-MM-DD'
            end_date: Fecha final en formato 'YYYY-MM-DD'
    
        Returns:
            Un DataFrame con meses en filas, países en columnas y la cantidad de usuarios como valores
        """

        # Convertir fechas de string a datetime para filtrar
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        end = end + timedelta(days=1)  # Incluir el último día completo

        # Consultar los documentos dentro del rango de fechas
        query = {
            "start_date": {
                "$gte": start.strftime('%Y-%m-%dT00:00:00.000-04:00'),
                "$lt": end.strftime('%Y-%m-%dT00:00:00.000-04:00')
            }
        }
    
        # Obtener solo los campos necesarios
        projection = {
            "start_date": 1,
            "user_id": 1,
            "_id": 0
        }
    
        # Ejecutar la consulta
        documents = list(self.collection.find(query, projection))
    
        # Procesar los resultados para obtener mes y país
        result_data = []
    
        for doc in documents:
            # Extraer solo la parte de la fecha y convertir a mes (YYYY-MM)
            date_str = doc["start_date"][:7]  # Toma solo YYYY-MM
        
            # Obtener el país a partir del número de teléfono
            user_phone = '+' + str(doc["user_id"])
            country = getCountry(user_phone)
        
            result_data.append({
                "month": date_str,
                "country": country
            })
    
        # Convertir a DataFrame
        df = pd.DataFrame(result_data)
    
        # Si no hay datos, devolver un DataFrame vacío
        if df.empty:
            return pd.DataFrame()
    
        # Contar por mes y país
        pivot_df = df.pivot_table(
            index="month", 
            columns="country", 
            aggfunc="size", 
            fill_value=0
        )
    
        # Asegurar que todos los meses en el rango tengan un valor
        # Crear un rango de meses desde start_date hasta end_date
        first_month = start.replace(day=1)
        last_month = end.replace(day=1)
        months = []
    
        current_month = first_month
        while current_month <= last_month:
            months.append(current_month.strftime('%Y-%m'))
            # Avanzar al siguiente mes
            if current_month.month == 12:
                current_month = current_month.replace(year=current_month.year + 1, month=1)
            else:
                current_month = current_month.replace(month=current_month.month + 1)
    
        # Crear un DataFrame con todos los meses
        complete_df = pd.DataFrame(index=months)
    
        # Unir con el pivot_df
        merged_df = complete_df.join(pivot_df, how='left').fillna(0).astype(int)
    
        return merged_df

    def daily_stripe_subs_by_country(self, start_date, end_date):
        """
        Cuenta la cantidad de usuarios que se registraron por día y por país en un rango de fechas.
    
        Args:
            start_date: Fecha de inicio en formato 'YYYY-MM-DD'
            end_date: Fecha final en formato 'YYYY-MM-DD'
        
        Returns:
            Un DataFrame con fechas en filas, países en columnas y la cantidad de usuarios como valores
        """
    
        # Convertir fechas de string a datetime para filtrar
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        end = end + timedelta(days=1)  # Incluir el último día completo
    
        # Consultar los documentos dentro del rango de fechas
        query = {
            "start_date": {
                "$gte": start.strftime('%Y-%m-%dT00:00:00.000-04:00'),
                "$lt": end.strftime('%Y-%m-%dT00:00:00.000-04:00')
            },
            "provider": "stripe"
        }
        
        # Obtener solo los campos necesarios
        projection = {
            "start_date": 1,
            "user_id": 1,
            "_id": 0
        }
        
        # Ejecutar la consulta
        documents = list(self.collection.find(query, projection))
        
        # Procesar los resultados para obtener fecha y país
        result_data = []
        
        for doc in documents:
            # Extraer solo la parte de la fecha (YYYY-MM-DD)
            date_str = doc["start_date"][:10]
            
            # Obtener el país a partir del número de teléfono
            user_phone = '+' + str(doc["user_id"] )
            country = getCountry(user_phone)
            
            result_data.append({
                "date": date_str,
                "country": country
            })
        
        # Convertir a DataFrame
        df = pd.DataFrame(result_data)
        
        # Si no hay datos, devolver un DataFrame vacío
        if df.empty:
            return pd.DataFrame()
        
        # Contar por fecha y país
        pivot_df = df.pivot_table(
            index="date", 
            columns="country", 
            aggfunc="size", 
            fill_value=0
        )
        
        # Asegurar que todas las fechas en el rango tengan un valor
        date_range = pd.date_range(start=start_date, end=end_date)
        date_range_str = [date.strftime('%Y-%m-%d') for date in date_range]
        
        # Crear un DataFrame con todas las fechas
        complete_df = pd.DataFrame(index=date_range_str)
        
        # Unir con el pivot_df
        merged_df = complete_df.join(pivot_df, how='left').fillna(0).astype(int)
        
        return merged_df
    
    def monthly_stripe_subs_by_country(self, start_date, end_date):
        """
        Cuenta la cantidad de usuarios que se registraron por mes y por país en un rango de fechas.

        Args:
            start_date: Fecha de inicio en formato 'YYYY-MM-DD'
            end_date: Fecha final en formato 'YYYY-MM-DD'
    
        Returns:
            Un DataFrame con meses en filas, países en columnas y la cantidad de usuarios como valores
        """

        # Convertir fechas de string a datetime para filtrar
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        end = end + timedelta(days=1)  # Incluir el último día completo

        # Consultar los documentos dentro del rango de fechas
        query = {
            "start_date": {
                "$gte": start.strftime('%Y-%m-%dT00:00:00.000-04:00'),
                "$lt": end.strftime('%Y-%m-%dT00:00:00.000-04:00')
            },
            "provider": "stripe"
        }
    
        # Obtener solo los campos necesarios
        projection = {
            "start_date": 1,
            "user_id": 1,
            "_id": 0
        }
    
        # Ejecutar la consulta
        documents = list(self.collection.find(query, projection))
    
        # Procesar los resultados para obtener mes y país
        result_data = []
    
        for doc in documents:
            # Extraer solo la parte de la fecha y convertir a mes (YYYY-MM)
            date_str = doc["start_date"][:7]  # Toma solo YYYY-MM
        
            # Obtener el país a partir del número de teléfono
            user_phone = '+' + str(doc["user_id"])
            country = getCountry(user_phone)
        
            result_data.append({
                "month": date_str,
                "country": country
            })
    
        # Convertir a DataFrame
        df = pd.DataFrame(result_data)
    
        # Si no hay datos, devolver un DataFrame vacío
        if df.empty:
            return pd.DataFrame()
    
        # Contar por mes y país
        pivot_df = df.pivot_table(
            index="month", 
            columns="country", 
            aggfunc="size", 
            fill_value=0
        )
    
        # Asegurar que todos los meses en el rango tengan un valor
        # Crear un rango de meses desde start_date hasta end_date
        first_month = start.replace(day=1)
        last_month = end.replace(day=1)
        months = []
    
        current_month = first_month
        while current_month <= last_month:
            months.append(current_month.strftime('%Y-%m'))
            # Avanzar al siguiente mes
            if current_month.month == 12:
                current_month = current_month.replace(year=current_month.year + 1, month=1)
            else:
                current_month = current_month.replace(month=current_month.month + 1)
    
        # Crear un DataFrame con todos los meses
        complete_df = pd.DataFrame(index=months)
    
        # Unir con el pivot_df
        merged_df = complete_df.join(pivot_df, how='left').fillna(0).astype(int)
    
        return merged_df

    def daily_mp_subs_by_country (self, start_date, end_date):
        """
        Cuenta la cantidad de usuarios que se registraron por día y por país en un rango de fechas.
    
        Args:
            start_date: Fecha de inicio en formato 'YYYY-MM-DD'
            end_date: Fecha final en formato 'YYYY-MM-DD'
        
        Returns:
            Un DataFrame con fechas en filas, países en columnas y la cantidad de usuarios como valores
        """
    
        # Convertir fechas de string a datetime para filtrar
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        end = end + timedelta(days=1)  # Incluir el último día completo
    
        # Consultar los documentos dentro del rango de fechas
        query = {
            "start_date": {
                "$gte": start.strftime('%Y-%m-%dT00:00:00.000-04:00'),
                "$lt": end.strftime('%Y-%m-%dT00:00:00.000-04:00')
            },
            "$or": [
                {"provider": {"$ne": "stripe"}},  # distinto de "stripe"
                {"provider": {"$exists": False}}  # o el campo no existe
            ]
        }
        
        # Obtener solo los campos necesarios
        projection = {
            "start_date": 1,
            "user_id": 1,
            "source": 1,
            "_id": 0
        }
        
        # Ejecutar la consulta
        documents = list(self.collection.find(query, projection))
        
        # Procesar los resultados para obtener fecha y país
        result_data = []
        
        for doc in documents:
            # Extraer solo la parte de la fecha (YYYY-MM-DD)
            date_str = doc["start_date"][:10]
            
            # Obtener el país a partir del número de teléfono
            if doc['source'] == "t":
                country = "Telegram"
            else:
                user_phone = '+' + str(doc["user_id"] )
                country = getCountry(user_phone)
            
            result_data.append({
                "date": date_str,
                "country": country
            })
        
        # Convertir a DataFrame
        df = pd.DataFrame(result_data)
        
        # Si no hay datos, devolver un DataFrame vacío
        if df.empty:
            return pd.DataFrame()
        
        # Contar por fecha y país
        pivot_df = df.pivot_table(
            index="date", 
            columns="country", 
            aggfunc="size", 
            fill_value=0
        )
        
        # Asegurar que todas las fechas en el rango tengan un valor
        date_range = pd.date_range(start=start_date, end=end_date)
        date_range_str = [date.strftime('%Y-%m-%d') for date in date_range]
        
        # Crear un DataFrame con todas las fechas
        complete_df = pd.DataFrame(index=date_range_str)
        
        # Unir con el pivot_df
        merged_df = complete_df.join(pivot_df, how='left').fillna(0).astype(int)
        
        return merged_df

    def monthly_mp_subs_by_country(self, start_date, end_date):
        """
        Cuenta la cantidad de usuarios que se registraron por mes y por país en un rango de fechas.

        Args:
            start_date: Fecha de inicio en formato 'YYYY-MM-DD'
            end_date: Fecha final en formato 'YYYY-MM-DD'
    
        Returns:
            Un DataFrame con meses en filas, países en columnas y la cantidad de usuarios como valores
        """

        # Convertir fechas de string a datetime para filtrar
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        end = end + timedelta(days=1)  # Incluir el último día completo

        # Consultar los documentos dentro del rango de fechas
        query = {
            "start_date": {
                "$gte": start.strftime('%Y-%m-%dT00:00:00.000-04:00'),
                "$lt": end.strftime('%Y-%m-%dT00:00:00.000-04:00')
            },
            "$or": [
                {"provider": {"$ne": "stripe"}},  # distinto de "stripe"
                {"provider": {"$exists": False}}  # o el campo no existe
            ]
        }
    
        # Obtener solo los campos necesarios
        projection = {
            "start_date": 1,
            "user_id": 1,
            "_id": 0
        }
    
        # Ejecutar la consulta
        documents = list(self.collection.find(query, projection))
    
        # Procesar los resultados para obtener mes y país
        result_data = []
    
        for doc in documents:
            # Extraer solo la parte de la fecha y convertir a mes (YYYY-MM)
            date_str = doc["start_date"][:7]  # Toma solo YYYY-MM
        
            # Obtener el país a partir del número de teléfono
            user_phone = '+' + str(doc["user_id"])
            country = getCountry(user_phone)
        
            result_data.append({
                "month": date_str,
                "country": country
            })
    
        # Convertir a DataFrame
        df = pd.DataFrame(result_data)
    
        # Si no hay datos, devolver un DataFrame vacío
        if df.empty:
            return pd.DataFrame()
    
        # Contar por mes y país
        pivot_df = df.pivot_table(
            index="month", 
            columns="country", 
            aggfunc="size", 
            fill_value=0
        )
    
        # Asegurar que todos los meses en el rango tengan un valor
        # Crear un rango de meses desde start_date hasta end_date
        first_month = start.replace(day=1)
        last_month = end.replace(day=1)
        months = []
    
        current_month = first_month
        while current_month <= last_month:
            months.append(current_month.strftime('%Y-%m'))
            # Avanzar al siguiente mes
            if current_month.month == 12:
                current_month = current_month.replace(year=current_month.year + 1, month=1)
            else:
                current_month = current_month.replace(month=current_month.month + 1)
    
        # Crear un DataFrame con todos los meses
        complete_df = pd.DataFrame(index=months)
    
        # Unir con el pivot_df
        merged_df = complete_df.join(pivot_df, how='left').fillna(0).astype(int)
    
        return merged_df

    def daily_subs(self, start_date, end_date):
        """
        Cuenta la cantidad de usuarios que se registraron por día en un rango de fechas.
    
        Args:
            start_date: Fecha de inicio en formato 'YYYY-MM-DD'
            end_date: Fecha final en formato 'YYYY-MM-DD'
        
        Returns:
            Un diccionario con fechas como claves y cantidad de usuarios como valores
        """
    
        # Convertir fechas de string a datetime para filtrar
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        end = end + timedelta(days=1)  # Incluir el último día completo
    
        # Crear pipeline de agregación para contar usuarios por día
        pipeline = [
            {
                # Filtrar documentos dentro del rango de fechas
                "$match": {
                    "start_date": {
                        "$gte": start.strftime('%Y-%m-%dT00:00:00.000-04:00'),
                        "$lt": end.strftime('%Y-%m-%dT00:00:00.000-04:00')
                    }
                }
            },
            {
                # Extraer solo la parte de la fecha (YYYY-MM-DD)
                "$addFields": {
                    "date_only": {
                        "$substr": ["$start_date", 0, 10]
                    }
                }
            },
            {
                # Agrupar por fecha y contar
                "$group": {
                    "_id": "$date_only",
                    "count": {"$sum": 1}
                }
            },
            {
                # Ordenar por fecha
                "$sort": {"_id": 1}
            }
        ]
    
        # Ejecutar la agregación
        result = list(self.collection.aggregate(pipeline))
    
        # Convertir resultado a diccionario fecha -> cantidad
        daily_counts = {doc["_id"]: doc["count"] for doc in result}
    
        # Asegurar que todas las fechas en el rango tengan un valor (incluso si es 0)
        current_date = start
        complete_daily_counts = {}
    
        while current_date < end:
            date_str = current_date.strftime('%Y-%m-%d')
            complete_daily_counts[date_str] = daily_counts.get(date_str, 0)
            current_date += timedelta(days=1)
    
        return complete_daily_counts
    
    def monthly_subs(self, start_date, end_date):
        """
        Cuenta la cantidad de usuarios que se registraron por mes en un rango de fechas.
    
        Args:
            start_date: Fecha de inicio en formato 'YYYY-MM-DD'
            end_date: Fecha final en formato 'YYYY-MM-DD'
        
        Returns:
            Un diccionario con meses como claves (formato 'YYYY-MM') y cantidad de usuarios como valores
        """
    
        # Convertir fechas de string a datetime para filtrar
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        end = end + timedelta(days=1)  # Incluir el último día completo
    
        # Crear pipeline de agregación para contar usuarios por mes
        pipeline = [
            {
                # Filtrar documentos dentro del rango de fechas
                "$match": {
                    "start_date": {
                        "$gte": start.strftime('%Y-%m-%dT00:00:00.000-04:00'),
                        "$lt": end.strftime('%Y-%m-%dT00:00:00.000-04:00')
                    }
                }
            },
            {
                # Extraer año y mes como 'YYYY-MM'
                "$addFields": {
                    "month_only": {
                        "$substr": ["$start_date", 0, 7]
                    }
                }
            },
            {
                # Agrupar por mes y contar
                "$group": {
                    "_id": "$month_only",
                    "count": {"$sum": 1}
                }
            },
            {
                # Ordenar por mes
                "$sort": {"_id": 1}
            }
        ]
    
        # Ejecutar la agregación
        result = list(self.collection.aggregate(pipeline))
    
        # Convertir resultado a diccionario mes -> cantidad
        monthly_counts = {doc["_id"]: doc["count"] for doc in result}
    
        # Asegurar que todos los meses en el rango tengan un valor (incluso si es 0)
        complete_monthly_counts = {}
    
        # Generar lista de todos los meses en el rango
        current_date = datetime(start.year, start.month, 1)
        end_month = datetime(end.year, end.month, 1)
    
        while current_date <= end_month:
            month_str = current_date.strftime('%Y-%m')
            complete_monthly_counts[month_str] = monthly_counts.get(month_str, 0)
        
            # Avanzar al siguiente mes
            if current_date.month == 12:
                current_date = datetime(current_date.year + 1, 1, 1)
            else:
                current_date = datetime(current_date.year, current_date.month + 1, 1)
    
        return complete_monthly_counts
    

    def daily_stripe_subs(self, start_date, end_date):
        """
        Cuenta la cantidad de suscriptores de Stripe por día en un rango de fechas.
    
        Args:
            start_date: Fecha de inicio en formato 'YYYY-MM-DD'
            end_date: Fecha final en formato 'YYYY-MM-DD'
        
        Returns:
        Un diccionario con fechas como claves y cantidad de suscriptores como valores
        """
        # Convertir fechas de string a datetime para filtrar
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        end = end + timedelta(days=1)  # Incluir el último día completo
    
        # Crear pipeline de agregación para contar suscriptores de Stripe por día
        pipeline = [
            {
                # Filtrar documentos de Stripe dentro del rango de fechas
                "$match": {
                    "provider": "stripe",
                    "start_date": {
                        "$gte": start.strftime('%Y-%m-%dT00:00:00.000Z'),
                        "$lt": end.strftime('%Y-%m-%dT00:00:00.000Z')
                    }
                }
            },
            {
                # Extraer solo la parte de la fecha (YYYY-MM-DD)
                "$addFields": {
                    "date_only": {
                        "$substr": ["$start_date", 0, 10]
                    }
                }
            },
            {
                # Agrupar por fecha y contar
                "$group": {
                    "_id": "$date_only",
                    "count": {"$sum": 1}
                }
            },
            {
                # Ordenar por fecha
                "$sort": {"_id": 1}
            }
        ]
    
        # Ejecutar la agregación
        result = list(self.collection.aggregate(pipeline))
    
        # Convertir resultado a diccionario fecha -> cantidad
        daily_counts = {doc["_id"]: doc["count"] for doc in result}
    
        # Asegurar que todas las fechas en el rango tengan un valor (incluso si es 0)
        current_date = start
        complete_daily_counts = {}
    
        while current_date < end:
            date_str = current_date.strftime('%Y-%m-%d')
            complete_daily_counts[date_str] = daily_counts.get(date_str, 0)
            current_date += timedelta(days=1)
        return complete_daily_counts
    
    
    def monthly_stripe_subs(self, start_date, end_date):
        """
        Cuenta la cantidad de suscriptores de Stripe por mes en un rango de fechas.
    
        Args:
            start_date: Fecha de inicio en formato 'YYYY-MM-DD'
            end_date: Fecha final en formato 'YYYY-MM-DD'
        
        Returns:
            Un diccionario con meses como claves (formato 'YYYY-MM') y cantidad de suscriptores como valores
        """
    
        # Convertir fechas de string a datetime para filtrar
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        end = end + timedelta(days=1)  # Incluir el último día completo
    
        # Crear pipeline de agregación para contar suscriptores de Stripe por mes
        pipeline = [
            {
                # Filtrar documentos de Stripe dentro del rango de fechas
                "$match": {
                    "provider": "stripe",
                    "start_date": {
                        "$gte": start.strftime('%Y-%m-%dT00:00:00.000Z'),
                        "$lt": end.strftime('%Y-%m-%dT00:00:00.000Z')
                    }
                }
            },
            {
                # Extraer año y mes como 'YYYY-MM'
                "$addFields": {
                    "month_only": {
                        "$substr": ["$start_date", 0, 7]
                    }
                }
            },
            {
                # Agrupar por mes y contar
                "$group": {
                    "_id": "$month_only",
                    "count": {"$sum": 1}
                }
            },
            {
                # Ordenar por mes
                "$sort": {"_id": 1}
            }
        ]
    
        # Ejecutar la agregación
        result = list(self.collection.aggregate(pipeline))
    
        # Convertir resultado a diccionario mes -> cantidad
        monthly_counts = {doc["_id"]: doc["count"] for doc in result}
    
        # Asegurar que todos los meses en el rango tengan un valor (incluso si es 0)
        complete_monthly_counts = {}
    
        # Generar lista de todos los meses en el rango
        current_date = datetime(start.year, start.month, 1)
        end_month = datetime(end.year, end.month, 1)
    
        while current_date <= end_month:
            month_str = current_date.strftime('%Y-%m')
            complete_monthly_counts[month_str] = monthly_counts.get(month_str, 0)
        
            # Avanzar al siguiente mes
            if current_date.month == 12:
                current_date = datetime(current_date.year + 1, 1, 1)
            else:
                current_date = datetime(current_date.year, current_date.month + 1, 1)
    
        return complete_monthly_counts
    
    
    def daily_mp_subs(self, start_date, end_date):
        """
        Cuenta la cantidad de suscriptores que NO son de Stripe por día en un rango de fechas.
    
        Args:
            start_date: Fecha de inicio en formato 'YYYY-MM-DD'
            end_date: Fecha final en formato 'YYYY-MM-DD'
        
        Returns:
            Un diccionario con fechas como claves y cantidad de suscriptores como valores
        """
    
        # Convertir fechas de string a datetime para filtrar
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        end = end + timedelta(days=1)  # Incluir el último día completo
    
        # Crear pipeline de agregación para contar suscriptores que NO son de Stripe por día
        pipeline = [
            {
                # Filtrar documentos que NO son de Stripe dentro del rango de fechas
                "$match": {
                    "provider": {"$ne": "stripe"},
                    "start_date": {
                        "$gte": start.strftime('%Y-%m-%dT00:00:00.000Z'),
                        "$lt": end.strftime('%Y-%m-%dT00:00:00.000Z')
                    }
                }
            },
            {
                # Extraer solo la parte de la fecha (YYYY-MM-DD)
                "$addFields": {
                    "date_only": {
                        "$substr": ["$start_date", 0, 10]
                    }
                }
            },
            {
                # Agrupar por fecha y contar
                "$group": {
                    "_id": "$date_only",
                    "count": {"$sum": 1}
                }
            },
            {
                # Ordenar por fecha
                "$sort": {"_id": 1}
            }
        ]
    
        # Ejecutar la agregación
        result = list(self.collection.aggregate(pipeline))
    
        # Convertir resultado a diccionario fecha -> cantidad
        daily_counts = {doc["_id"]: doc["count"] for doc in result}
    
        # Asegurar que todas las fechas en el rango tengan un valor (incluso si es 0)
        current_date = start
        complete_daily_counts = {}
    
        while current_date < end:
            date_str = current_date.strftime('%Y-%m-%d')
            complete_daily_counts[date_str] = daily_counts.get(date_str, 0)
            current_date += timedelta(days=1)
    
        return complete_daily_counts
    
    def monthly_mp_subs(self, start_date, end_date):
        """
        Cuenta la cantidad de suscriptores que NO son de Stripe por mes en un rango de fechas.
    
        Args:
            start_date: Fecha de inicio en formato 'YYYY-MM-DD'
            end_date: Fecha final en formato 'YYYY-MM-DD'
        
        Returns:
            Un diccionario con meses como claves (formato 'YYYY-MM') y cantidad de suscriptores como valores
        """
    
        # Convertir fechas de string a datetime para filtrar
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        end = end + timedelta(days=1)  # Incluir el último día completo
    
        # Crear pipeline de agregación para contar suscriptores que NO son de Stripe por mes
        pipeline = [
            {
                # Filtrar documentos que NO son de Stripe dentro del rango de fechas
                "$match": {
                    "provider": {"$ne": "stripe"},
                    "start_date": {
                        "$gte": start.strftime('%Y-%m-%dT00:00:00.000Z'),
                        "$lt": end.strftime('%Y-%m-%dT00:00:00.000Z')
                    }
                }
            },
            {
                # Extraer año y mes como 'YYYY-MM'
                "$addFields": {
                    "month_only": {
                        "$substr": ["$start_date", 0, 7]
                    }
                }
            },
            {
                # Agrupar por mes y contar
                "$group": {
                    "_id": "$month_only",
                    "count": {"$sum": 1}
                }
            },  
            {
                # Ordenar por mes
                "$sort": {"_id": 1}
            }
        ]
    
        # Ejecutar la agregación
        result = list(self.collection.aggregate(pipeline))
    
        # Convertir resultado a diccionario mes -> cantidad
        monthly_counts = {doc["_id"]: doc["count"] for doc in result}
    
        # Asegurar que todos los meses en el rango tengan un valor (incluso si es 0)
        complete_monthly_counts = {}
    
        # Generar lista de todos los meses en el rango
        current_date = datetime(start.year, start.month, 1)
        end_month = datetime(end.year, end.month, 1)
    
        while current_date <= end_month:
            month_str = current_date.strftime('%Y-%m')
            complete_monthly_counts[month_str] = monthly_counts.get(month_str, 0)
        
            # Avanzar al siguiente mes
            if current_date.month == 12:
                current_date = datetime(current_date.year + 1, 1, 1)
            else:
                current_date = datetime(current_date.year, current_date.month + 1, 1)
    
        return complete_monthly_counts
    
    def total_subs(self, start_date, end_date):
        """Cuenta el total de suscripciones usando daily_subs."""
        data = self.daily_subs(start_date, end_date)
        return sum(data.values())

    def average_daily_subs(self, start_date, end_date):
        """Promedio de suscripciones por día."""
        data = self.daily_subs(start_date, end_date)
        if not data:
            return 0
        return round(sum(data.values()) / len(data), 2)

    def average_monthly_subs(self, start_date, end_date):
        """Promedio mensual de suscripciones."""
        monthly_data = self.monthly_subs(start_date, end_date)
        if len(monthly_data) == 0:
            return 0
        return round(sum(monthly_data.values()) / len(monthly_data), 2)
    
    def total_stripe_subs(self, start_date, end_date):
        """Cuenta el total de suscripciones usando daily_subs."""
        data = self.daily_stripe_subs(start_date, end_date)
        return sum(data.values())

    def average_stripe_daily_subs(self, start_date, end_date):
        """Promedio de suscripciones por día."""
        data = self.daily_stripe_subs(start_date, end_date)
        if not data:
            return 0
        return round(sum(data.values()) / len(data), 2)

    def average_stripe_monthly_subs(self, start_date, end_date):
        """Promedio mensual de suscripciones."""
        monthly_data = self.monthly_stripe_subs(start_date, end_date)
        if len(monthly_data) == 0:
            return 0
        return round(sum(monthly_data.values()) / len(monthly_data), 2)
    
    def total_mp_subs(self, start_date, end_date):
        """Cuenta el total de suscripciones usando daily_subs."""
        data = self.daily_mp_subs(start_date, end_date)
        return sum(data.values())

    def average_mp_daily_subs(self, start_date, end_date):
        """Promedio de suscripciones por día."""
        data = self.daily_mp_subs(start_date, end_date)
        if not data:
            return 0
        return round(sum(data.values()) / len(data), 2)

    def average_mp_monthly_subs(self, start_date, end_date):
        """Promedio mensual de suscripciones."""
        monthly_data = self.monthly_mp_subs(start_date, end_date)
        if len(monthly_data) == 0:
            return 0
        return round(sum(monthly_data.values()) / len(monthly_data), 2)

    def total_subs(self, start_date, end_date):
        """Cuenta el total de suscripciones usando daily_subs."""
        data = self.daily_subs(start_date, end_date)
        return sum(data.values())

    def average_daily_subs(self, start_date, end_date):
        """Promedio de suscripciones por día."""
        data = self.daily_subs(start_date, end_date)
        if not data:
            return 0
        return round(sum(data.values()) / len(data), 2)

    def average_monthly_subs(self, start_date, end_date):
        """Promedio mensual de suscripciones."""
        monthly_data = self.monthly_subs(start_date, end_date)
        if len(monthly_data) == 0:
            return 0
        return round(sum(monthly_data.values()) / len(monthly_data), 2)
    
    def total_stripe_subs(self, start_date, end_date):
        """Cuenta el total de suscripciones usando daily_subs."""
        data = self.daily_stripe_subs(start_date, end_date)
        return sum(data.values())

    def average_stripe_daily_subs(self, start_date, end_date):
        """Promedio de suscripciones por día."""
        data = self.daily_stripe_subs(start_date, end_date)
        if not data:
            return 0
        return round(sum(data.values()) / len(data), 2)

    def average_stripe_monthly_subs(self, start_date, end_date):
        """Promedio mensual de suscripciones."""
        monthly_data = self.monthly_stripe_subs(start_date, end_date)
        if len(monthly_data) == 0:
            return 0
        return round(sum(monthly_data.values()) / len(monthly_data), 2)
    
    def total_mp_subs(self, start_date, end_date):
        """Cuenta el total de suscripciones usando daily_subs."""
        data = self.daily_mp_subs(start_date, end_date)
        return sum(data.values())

    def average_mp_daily_subs(self, start_date, end_date):
        """Promedio de suscripciones por día."""
        data = self.daily_mp_subs(start_date, end_date)
        if not data:
            return 0
        return round(sum(data.values()) / len(data), 2)

    def average_mp_monthly_subs(self, start_date, end_date):
        """Promedio mensual de suscripciones."""
        monthly_data = self.monthly_mp_subs(start_date, end_date)
        if len(monthly_data) == 0:
            return 0
        return round(sum(monthly_data.values()) / len(monthly_data), 2)
    
    def contar_suscripciones_mercado_pago(self):
        """
        Cuenta la cantidad de suscripciones de Mercado Pago por tipo,
        identificándolas por la ausencia del campo "provider": "stripe"
        y analizando los campos "source" y "reason".

        Args:
            self: La instancia de la base de datos de MongoDB.

        Returns:
            Una lista de diccionarios, donde cada diccionario tiene una clave
            que representa el tipo de suscripción y un valor que indica la cantidad.
        """
        pipeline = [
            {"$match": {"provider": {"$ne": "stripe"}}},
            {"$project": {
                "tipo": {
                    "$switch": {
                        "branches": [
                            {"case": {"$eq": ["$source", "wc"]}, "then": "Chomky"},
                            {"case": {"$eq": ["$reason", 'TranscribeMe Plus discount']}, "then": 'TranscribeMe Plus discount'},
                            {"case": {"$eq": ["$reason", 'TranscribeMe Plus - mensual 20% off']}, "then": 'TranscribeMe Plus - mensual 20% off'},
                            {"case": {"$eq": ["$reason", "TranscribeMe Plus"]}, "then": "TranscribeMe Plus"},
                            {"case": {"$eq": ["$reason", "TranscribeMe Plus 2"]}, "then": "TranscribeMe Plus 2"},
                            {"case": {"$eq": ["$reason", "TranscribeMe Plus 10d"]}, "then": "TranscribeMe Plus 10d"},
                            {"case": {"$eq": ["$reason", 'TranscribeMe Plus - Anual con 3 meses gratis']}, "then": 'TranscribeMe Plus - Anual con 3 meses gratis'},
                            {"case": {"$eq": ["$reason", "hearing impairment"]}, "then": "Discapacidad Auditiva"},
                            {"case": {"$eq": ["$reason", "free-granted"]}, "then": "Gratis"},
                            {"case": {"$eq": ["$provider", "manual"]}, "then": "Manual"},
                            {"case": {"$eq": ["$provider", "mp_discount"]}, "then": "Pago por 3 meses"},
                        ],
                        "default": "Otro"
                    }
                },
                "_id": 0
            }},
            {"$group": {"_id": "$tipo", "cantidad": {"$sum": 1}}},
            {"$project": {"tipo": "$_id", "cantidad": 1, "_id": 0}}
        ]

        return list(self.collection.aggregate(pipeline))

    
    def status_stripe_subs (self):
        """Status actual de las suscripciones de Stripe"""
        pipeline = [
        {"$match": {"provider": "stripe"}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
        ]   
        return list(self.collection.aggregate(pipeline))

    def status_tme_plus (self):
        """Status actual de las suscripciones del plan TranscribeMe Plus"""
        pipeline = [
        {"$match": {"reason": "TranscribeMe Plus"}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
        ]   
        return list(self.collection.aggregate(pipeline))

    def status_tme_plus2 (self):
        """Status actual de las suscripciones del plan TranscribeMe Plus 2"""
        pipeline = [
        {"$match": {"reason": "TranscribeMe Plus 2"}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
        ]   
        return list(self.collection.aggregate(pipeline))
    
    def total_active_subs(self):
        """Cuenta todas las suscripciones con status 'active' o 'authorized'"""
        query = {
            "status": {"$in": ["active", "authorized"]}
        }
        return self.collection.count_documents(query)

    
    def active_stripe_subs(self):
        """Devuelve la cantidad de suscripciones activas de Stripe"""
        query = {"provider": "stripe", "status": "active"}
        return self.collection.count_documents(query)
    
    def authorized_mp_subs(self):
        """Cuenta suscripciones autorizadas que no sean de Stripe o no tengan 'provider'"""
        query = {
            "$and": [
                {
                    "$or": [
                        {"provider": {"$ne": "stripe"}},
                        {"provider": {"$exists": False}}
                    ]
                },
                {"status": "authorized"}
            ]
        }
        return self.collection.count_documents(query)
