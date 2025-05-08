import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB_ANALYTICS, MONGO_COLLECTION_DAU
from user_metrics import UserMetrics
from datetime import date

# Inicializar la aplicación Dash
app = dash.Dash(__name__, title="Dashboard de Métricas de TME")

# Crear instancias de métricas
metrics = UserMetrics()

# Diseño del dashboard
app.layout = html.Div([
    html.H1("Dashboard de Métricas de Usuarios", style={'textAlign': 'center'}),
    
    # Selector de rango de fechas
    html.Div([
        html.Label("Seleccione un rango de fechas:"),
        dcc.DatePickerRange(
        id='date-range',
        start_date=date(2025, 5, 1),
        end_date=date.today(),
        display_format='YYYY-MM-DD',
        style={"marginBottom": "40px"}
    ),
    ], style={'margin': '20px'}),
    
    # Tarjetas de Métricas Clave
    html.Div([
        html.Div([
            html.H3("Total de Usuarios", style={'textAlign': 'center'}),
            html.Div(id='total-users-card', style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'flex': '1', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '15px', 'margin': '10px'}),
        
        html.Div([
            html.H3("Nuevos Usuarios (Período)", style={'textAlign': 'center'}),
            html.Div(id='new-users-card', style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'flex': '1', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '15px', 'margin': '10px'}),
        
        html.Div([
            html.H3("Promedio DAU (Período)", style={'textAlign': 'center'}),
            html.Div(id='avg-dau-card', style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'flex': '1', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '15px', 'margin': '10px'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'margin': '20px'}),
    
    # Gráficos
    html.Div([
        # Primera fila
        html.Div([
            html.Div([
                html.H3("Usuarios Activos Diarios", style={'textAlign': 'center'}),
                dcc.Graph(id='dau-graph')
            ], style={'flex': '1', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '15px', 'margin': '10px'}),
            
            html.Div([
                html.H3("Usuarios Activos Mensuales", style={'textAlign': 'center'}),
                dcc.Graph(id='mau-graph')
            ], style={'flex': '1', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '15px', 'margin': '10px'})
        ], style={'display': 'flex', 'justifyContent': 'space-between'}),
        
        # Segunda fila
        html.Div([
            html.Div([
                html.H3("Nuevos Usuarios por Día", style={'textAlign': 'center'}),
                dcc.Graph(id='new-users-day-graph')
            ], style={'flex': '1', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '15px', 'margin': '10px'}),
            
            html.Div([
                html.H3("Nuevos Usuarios por Mes", style={'textAlign': 'center'}),
                dcc.Graph(id='new-users-month-graph')
            ], style={'flex': '1', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '15px', 'margin': '10px'})
        ], style={'display': 'flex', 'justifyContent': 'space-between'})
    ], style={'margin': '20px'})
])

# Definir callbacks
@callback(
    [Output('dau-graph', 'figure'),
     Output('mau-graph', 'figure'),
     Output('new-users-day-graph', 'figure'),
     Output('new-users-month-graph', 'figure'),
     Output('total-users-card', 'children'),
     Output('new-users-card', 'children'),
     Output('avg-dau-card', 'children')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graphs(start_date, end_date):
    # Convertir fechas a datetime
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Obtener datos
    dau_data = metrics.get_daily_active_users(start_date, end_date)
    mau_data = metrics.get_monthly_active_users(start_date, end_date)
    new_users_day = metrics.get_new_users_by_day(start_date, end_date)
    new_users_month = metrics.get_new_users_by_month(start_date, end_date)
    total_users = metrics.get_total_users(end_date)
    
    # Convertir a DataFrames para facilitar la visualización
    dau_df = pd.DataFrame(dau_data)
    mau_df = pd.DataFrame(mau_data)
    new_users_day_df = pd.DataFrame(new_users_day)
    new_users_month_df = pd.DataFrame(new_users_month)
    
    # Gráfico de DAU
    dau_fig = px.line(
        dau_df, 
        x='date', 
        y='active_users',
        labels={'date': 'Fecha', 'active_users': 'Usuarios Activos Diarios'},
        title='Usuarios Activos Diarios (DAU)'
    )
    dau_fig.update_layout(hovermode='x unified')
    
    # Gráfico de MAU
    mau_fig = px.bar(
        mau_df, 
        x='month', 
        y='active_users',
        labels={'month': 'Mes', 'active_users': 'Usuarios Activos Mensuales'},
        title='Usuarios Activos Mensuales (MAU)'
    )
    
    # Gráfico de nuevos usuarios por día
    new_day_fig = px.line(
        new_users_day_df, 
        x='date', 
        y='new_users',
        labels={'date': 'Fecha', 'new_users': 'Nuevos Usuarios'},
        title='Nuevos Usuarios por Día'
    )
    new_day_fig.update_layout(hovermode='x unified')
    
    # Gráfico de nuevos usuarios por mes
    new_month_fig = px.bar(
        new_users_month_df, 
        x='month', 
        y='new_users',
        labels={'month': 'Mes', 'new_users': 'Nuevos Usuarios'},
        title='Nuevos Usuarios por Mes'
    )
    
    # Calcular métricas para tarjetas
    total_new_users = sum(item['new_users'] for item in new_users_day) if new_users_day else 0
    avg_dau = round(sum(item['active_users'] for item in dau_data) / len(dau_data), 1) if dau_data else 0
    
    return dau_fig, mau_fig, new_day_fig, new_month_fig, f"{total_users:,}", f"{total_new_users:,}", f"{avg_dau:,}"

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)